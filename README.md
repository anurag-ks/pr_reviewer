# AI PR Reviewer

An intelligent Pull Request review agent that uses AI to analyze code changes and provide detailed feedback on code quality, security, and best practices.

## Features

- Automated code review using AI language models
- Analysis of code quality, security, performance, and maintainability
- Language-agnostic code review capabilities
- Detailed feedback with specific examples and suggestions
- GitHub integration for seamless PR review process
- GitHub Actions integration for automated reviews

## Setup

### Prerequisites

- Python 3.8 or higher
- GitHub account and personal access token
- OpenAI API key

### Manual Usage

1. Clone the repository and install dependencies:
```bash
git clone https://github.com/yourusername/ai-pr-reviewer.git
cd ai-pr-reviewer
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
# Create a .env file or export to your environment
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_api_key
```

3. Run the reviewer:
```bash
python run_reviewer.py --repo owner/repo --pr 123
```

### GitHub Actions Integration

1. Add the workflow file to your repository:
   - Copy `.github/workflows/pr-review.yml` to your repository's `.github/workflows/` directory

2. Configure repository secrets:
   - Navigate to Settings > Secrets and Variables > Actions
   - Add required secrets:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `GITHUB_TOKEN`: Automatically provided by GitHub Actions

The reviewer will automatically run on:
- New pull request creation
- Pull request updates
- Reopening of closed pull requests

## Configuration

Customize the review behavior in `config.py`:
- File review limits
- Change size thresholds
- Review focus areas
- Language-specific settings

## Review Output

The reviewer provides comprehensive feedback including:
- Code quality assessment
- Security analysis
- Performance optimization suggestions
- Maintainability recommendations
- Testing considerations

## Contributing

Contributions are welcome! Please feel free to:
- Submit issues
- Create pull requests
- Suggest improvements
- Report bugs
