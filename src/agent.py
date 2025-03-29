import os
import logging
from typing import List, Dict, Any
import aiohttp
from github import Github
from pydantic import BaseModel
import openai
from datetime import datetime
import asyncio
from functools import partial

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the API keys in the environment variables
os.environ['GITHUB_TOKEN'] = 'xxx'
os.environ['OPENAI_API_KEY'] = 'xxx'


class PRReviewConfig(BaseModel):
    """Configuration for PR review settings"""
    max_files_to_review: int = 50
    max_changes_per_file: int = 500
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.3
    batch_size: int = 5
    review_categories: List[str] = [
        "code_quality",
        "security",
        "performance",
        "maintainability",
        "testing"
    ]
    language_specific_rules: Dict[str, List[str]] = {
        "python": [
            "PEP 8 compliance",
            "Type hints",
            "Docstrings",
            "Error handling",
            "Code complexity"
        ],
        "javascript": [
            "ESLint rules",
            "Modern ES6+ features",
            "Error handling",
            "Code organization"
        ]
    }
    ignore_patterns: List[str] = [
        "*.lock",
        "*.md",
        "*.txt"
    ]

class PRReviewer:
    def __init__(self, github_token: str = None, openai_api_key: str = None):
        """Initialize the PR reviewer with necessary credentials"""
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.github_token or not self.openai_api_key:
            raise ValueError("GitHub token and OpenAI API key are required")
        
        self.github = Github(self.github_token, retry=3)
        self.config = PRReviewConfig()
        self.session = None
        self.openai_client = None

    async def __aenter__(self):
        """Initialize async resources when entering context"""
        self.session = aiohttp.ClientSession()
        self.openai_client = openai.AsyncOpenAI(api_key=self.openai_api_key)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup async resources when exiting context"""
        if self.session:
            await self.session.close()
        if self.openai_client:
            await self.openai_client.close()

    async def _run_in_executor(self, func, *args, **kwargs):
        """Run synchronous code in executor"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, partial(func, *args, **kwargs))

    async def fetch_pr_details(self, repo_name: str, pr_number: int) -> Dict[str, Any]:
        """Fetch PR details from GitHub"""
        try:
            # Run GitHub operations in executor since they're blocking
            repo = await self._run_in_executor(self.github.get_repo, repo_name)
            pr = await self._run_in_executor(repo.get_pull, pr_number)
            
            files = await self._run_in_executor(lambda: [f.filename for f in pr.get_files()])
            
            return {
                "title": pr.title,
                "description": pr.body,
                "files": files,
                "base_branch": pr.base.ref,
                "head_branch": pr.head.ref,
                "created_at": pr.created_at,
                "updated_at": pr.updated_at
            }
        except Exception as e:
            logger.error(f"Error fetching PR details: {str(e)}")
            raise

    async def _analyze_file(self, repo, pr, file):
        """Analyze a single file's changes"""
        try:
            # Get file content in executor
            content = await self._run_in_executor(
                repo.get_contents,
                file.filename,
                ref=pr.head.ref
            )
            
            file_content = content.decoded_content.decode('utf-8') if hasattr(content, 'decoded_content') else ""
            
            return await self._analyze_file_content(
                file_content,
                file.filename,
                file.patch or ""
            )
        except Exception as e:
            logger.error(f"Error analyzing file {file.filename}: {str(e)}")
            return {
                "filename": file.filename,
                "analysis": f"Error analyzing file: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def analyze_code_changes(self, repo_name: str, pr_number: int) -> List[Dict[str, Any]]:
        """Analyze code changes in the PR"""
        try:
            repo = await self._run_in_executor(self.github.get_repo, repo_name)
            pr = await self._run_in_executor(repo.get_pull, pr_number)
            
            files = await self._run_in_executor(lambda: list(pr.get_files()))
            files = files[:self.config.max_files_to_review]  # Limit number of files
            
            reviews = []
            # Process files in batches
            for i in range(0, len(files), self.config.batch_size):
                batch = files[i:i + self.config.batch_size]
                tasks = [self._analyze_file(repo, pr, file) for file in batch]
                batch_reviews = await asyncio.gather(*tasks, return_exceptions=True)
                reviews.extend([r for r in batch_reviews if not isinstance(r, Exception)])
            
            return reviews
        except Exception as e:
            logger.error(f"Error analyzing code changes: {str(e)}")
            raise

    async def _analyze_file_content(self, content: str, filename: str, patch: str) -> Dict[str, Any]:
        """Analyze individual file content using OpenAI"""
        try:
            file_ext = filename.split('.')[-1].lower()
            language_rules = self.config.language_specific_rules.get(file_ext, [])
            
            prompt = f"""
            Review the following code changes and provide feedback on:
            1. Code quality and best practices
            2. Potential security issues
            3. Performance considerations
            4. Maintainability
            5. Testing coverage
            
            File: {filename}
            Language: {file_ext}
            Specific rules to check: {', '.join(language_rules)}
            
            Code changes:
            {patch}
            
            Please provide structured feedback with specific examples and suggestions for improvement.
            """
            
            response = await self.openai_client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer focusing on code quality, security, and best practices."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.openai_temperature
            )
            
            return {
                "filename": filename,
                "analysis": response.choices[0].message.content,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error analyzing file content for {filename}: {str(e)}")
            raise

    async def post_review(self, repo_name: str, pr_number: int, reviews: List[Dict[str, Any]]):
        """Post review comments on the PR"""
        try:
            repo = await self._run_in_executor(self.github.get_repo, repo_name)
            pr = await self._run_in_executor(repo.get_pull, pr_number)
            
            review_body = "## AI Code Review Summary\n\n"
            for review in reviews:
                review_body += f"### {review['filename']}\n{review['analysis']}\n\n"
            
            await self._run_in_executor(
                pr.create_review,
                body=review_body,
                event="COMMENT"
            )
            
            logger.info(f"Successfully posted review for PR #{pr_number}")
        except Exception as e:
            logger.error(f"Error posting review: {str(e)}")
            raise

    async def review_pr(self, repo_name: str, pr_number: int):
        """Main method to review a PR"""
        try:
            pr_details = await self.fetch_pr_details(repo_name, pr_number)
            logger.info(f"Fetched details for PR #{pr_number}")
            
            reviews = await self.analyze_code_changes(repo_name, pr_number)
            logger.info(f"Analyzed {len(reviews)} files")
            
            await self.post_review(repo_name, pr_number, reviews)
            logger.info("Review completed successfully")
            
        except Exception as e:
            logger.error(f"Error in PR review process: {str(e)}")
            raise 