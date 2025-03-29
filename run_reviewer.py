import asyncio
import argparse
import os
from src.agent import PRReviewer

async def main():
    parser = argparse.ArgumentParser(description='Review GitHub PR')
    parser.add_argument('--repo', required=True, help='Repository name (owner/repo)')
    parser.add_argument('--pr', required=True, type=int, help='PR number')
    args = parser.parse_args()

    async with PRReviewer() as reviewer:
        await reviewer.review_pr(args.repo, args.pr)

if __name__ == "__main__":
    asyncio.run(main()) 