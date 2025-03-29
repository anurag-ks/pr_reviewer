# AI PR Reviewer

An intelligent Pull Request review agent that uses AI to analyze code changes and provide detailed feedback on code quality, security, and best practices.

## Features

- Automated code review using OpenAI's GPT-4
- Analysis of code quality, security, performance, and maintainability
- Language-specific rule checking (currently supports Python)
- Detailed feedback with specific examples and suggestions
- GitHub integration for seamless PR review process
- GitHub Actions integration for automated reviews

## Setup

### Manual Usage

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables:
```bash
export GITHUB_TOKEN=your_github_token
export OPENAI_API_KEY=your_openai_api_key
```

Or provide them as command-line arguments when running the script.

3. Run the reviewer:
```bash
python run_reviewer.py --repo owner/repo --pr-number 123
```

### GitHub Actions Integration

1. Copy the `.github/workflows/pr-review.yml` file to your repository's `.github/workflows/` directory.

2. Add the following secrets to your GitHub repository:
   - Go to your repository settings
   - Navigate to Secrets and Variables > Actions
   - Add the following secrets:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `GITHUB_TOKEN`: This is automatically provided by GitHub Actions

3. The PR reviewer will now automatically run when:
   - A new pull request is opened
   - A pull request is updated with new commits
   - A closed pull request is reopened

## Configuration

You can customize the review settings by modifying the `PRReviewConfig` class in `agent.py`. Current settings include:

- Maximum number of files to review
- Maximum changes per file
- Review categories
- Language-specific rules

## Example Output

The reviewer will post a comment on the PR with a structured review that includes:

1. Code quality analysis
2. Security considerations
3. Performance recommendations
4. Maintainability suggestions
5. Testing coverage feedback

## Contributing

Feel free to submit issues and enhancement requests! 