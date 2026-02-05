#!/usr/bin/env python3
"""
AI-powered code review script that analyzes PR diffs and posts detailed feedback.
"""

import os
import sys
import argparse
from typing import List
import openai
from github import Github

# Review prompt template
REVIEW_PROMPT = """
You are an expert code reviewer for a FastAPI + React TypeScript application.
Review the following code changes and provide constructive feedback.

Focus on:
1. Security vulnerabilities (SQL injection, XSS, auth issues)
2. Performance issues (N+1 queries, inefficient algorithms)
3. Best practices violations (FastAPI, React, TypeScript)
4. Code quality (naming, structure, readability)
5. Test coverage (are there tests for new code?)
6. Error handling (proper exception handling)
7. Type safety (TypeScript types, Python type hints)

Changed files:
{changed_files}

Diff (first 8000 chars):
{diff_content}

Provide feedback in this format:
## Summary
Brief overview of the changes and overall quality.

## Critical Issues 🔴
Issues that must be fixed before merge.

## Suggestions 🟡
Recommendations for improvement.

## Positive Observations ✅
Things done well.

Keep feedback specific, actionable, and constructive.
"""


def analyze_code_with_ai(diff_content: str, changed_files: List[str], api_key: str) -> str:
    """Send code diff to OpenAI for review."""
    client = openai.OpenAI(api_key=api_key)

    prompt = REVIEW_PROMPT.format(
        changed_files="\n".join(changed_files),
        diff_content=diff_content[:8000],  # Limit diff size
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert code reviewer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=2000,
    )

    return response.choices[0].message.content


def post_review_comment(pr_number: int, review_content: str, github_token: str, repo_name: str):
    """Post AI review as a PR comment."""
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    comment_body = f"""## 🤖 AI Code Review

{review_content}

---
*This review was generated automatically. Please use your judgment and human review for final decisions.*
"""

    pr.create_issue_comment(comment_body)


def main():
    parser = argparse.ArgumentParser(description="AI-powered code review")
    parser.add_argument("--pr-number", type=int, required=True)
    parser.add_argument("--diff-file", required=True)
    parser.add_argument("--changed-files", required=True)
    args = parser.parse_args()

    # Read diff and changed files
    with open(args.diff_file, "r") as f:
        diff_content = f.read()

    with open(args.changed_files, "r") as f:
        changed_files = [line.strip() for line in f if line.strip()]

    # Skip if diff is too small or too large
    if len(diff_content) < 50:
        print("Diff too small, skipping review")
        return

    if len(diff_content) > 50000:
        print("Diff too large, truncating")
        diff_content = diff_content[:50000] + "\n... (truncated)"

    # Get API keys from environment
    openai_key = os.environ.get("OPENAI_API_KEY")
    github_token = os.environ.get("GITHUB_TOKEN")
    repo_name = os.environ.get("GITHUB_REPOSITORY")

    if not openai_key:
        print("⚠️ OPENAI_API_KEY not set, skipping AI review")
        return

    # Analyze with AI
    print(f"Analyzing {len(changed_files)} changed files...")
    review_content = analyze_code_with_ai(diff_content, changed_files, openai_key)

    # Post review
    print("Posting review comment...")
    post_review_comment(args.pr_number, review_content, github_token, repo_name)

    print("✅ AI review posted successfully")


if __name__ == "__main__":
    main()
