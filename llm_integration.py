"""
LLM Integration Module for Resume Assistant.

This file should stay backend-only. Streamlit UI code belongs in app.py.
"""

import json
import os
from typing import Dict

import requests
from dotenv import load_dotenv


class LLMResumeAssistant:
    """Handle interactions with LLM APIs for resume suggestions."""

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.provider = "gemini" if self.api_key else None
        self.key_source = "env" if self.api_key else None
        self.api_urls = {
            "claude": "https://api.anthropic.com/v1/messages",
            "openai": "https://api.openai.com/v1/chat/completions",
            "gemini": "https://generativelanguage.googleapis.com/v1beta/models",
        }
        self.gemini_models = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
        ]

    def set_api_key(self, api_key: str, provider: str = "gemini"):
        """Set API key and provider."""
        self.api_key = api_key
        self.provider = provider
        self.key_source = "manual"

    def _is_placeholder_key(self) -> bool:
        """Detect obviously fake/demo API keys."""
        if not self.api_key:
            return True

        normalized = self.api_key.strip()
        placeholder_markers = [
            "1234567890",
            "abcdef",
            "your_api_key",
            "replace_me",
            "example",
        ]
        return any(marker in normalized.lower() for marker in placeholder_markers)

    def has_valid_key(self) -> bool:
        """Return True when an API key is available and not an obvious placeholder."""
        return bool(self.api_key and self.api_key.strip()) and not self._is_placeholder_key()

    def get_key_status_message(self) -> str:
        """Return a short user-facing key status message."""
        if not self.api_key or not self.api_key.strip():
            return "No Gemini API key found."
        if self._is_placeholder_key():
            return "The configured Gemini API key looks like a placeholder/example key."
        return "Gemini API key detected."

    def clear_api_key(self):
        """Clear the in-memory key without touching .env on disk."""
        self.api_key = None
        self.provider = None
        self.key_source = None

    def _get_headers(self):
        """Get headers for API requests."""
        if self.provider == "claude":
            return {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
        if self.provider == "openai":
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        if self.provider == "gemini":
            return {"Content-Type": "application/json"}
        return {}

    def _build_prompt(self, context: Dict, user_request: str = None) -> str:
        """Build prompt for general resume feedback."""
        prompt = (
            "You are an expert resume coach and career advisor with 10+ years of "
            "experience in tech hiring.\n"
            "Your goal is to provide actionable, specific advice to improve resumes "
            "for ATS systems and human recruiters.\n\n"
        )

        if context.get("resume_text"):
            prompt += f"CURRENT RESUME:\n{context['resume_text'][:2000]}\n\n"

        if context.get("job_role"):
            prompt += f"TARGET JOB ROLE: {context['job_role']}\n\n"

        if context.get("ats_score") is not None:
            prompt += f"CURRENT ATS SCORE: {context['ats_score']}%\n\n"

        if context.get("matched_skills"):
            prompt += (
                "STRENGTHS (Matched Skills):\n"
                f"{', '.join(context['matched_skills'][:10])}\n\n"
            )

        if context.get("missing_skills"):
            prompt += (
                "GAPS (Missing Skills):\n"
                f"{', '.join(context['missing_skills'][:10])}\n\n"
            )

        if context.get("section_scores"):
            prompt += f"SECTION SCORES:\n{json.dumps(context['section_scores'], indent=2)}\n\n"

        if user_request:
            prompt += f"USER REQUEST: {user_request}\n\n"
        else:
            prompt += (
                "Please provide a comprehensive analysis with:\n"
                "1. Top 3 strengths of this resume\n"
                "2. Top 5 areas for improvement\n"
                "3. Specific, actionable suggestions to increase ATS score\n"
                "4. Examples of how to rewrite weak bullet points\n"
                "5. Industry-specific advice for this role\n\n"
                "Be specific, practical, and provide examples where possible.\n"
            )

        prompt += "\nRemember: Focus on actionable advice that the user can implement immediately."
        return prompt

    def _build_chat_prompt(self, user_message: str, context: Dict) -> str:
        """Build prompt for chat interaction."""
        prompt = (
            "You are an expert resume coach. You have access to the user's resume "
            "and analysis.\n"
            "Answer questions specifically about their resume, providing detailed, "
            "actionable advice.\n\n"
        )

        if context.get("resume_text"):
            prompt += f"USER'S RESUME:\n{context['resume_text'][:1500]}\n\n"

        if context.get("analysis_results"):
            analysis = context["analysis_results"]
            prompt += (
                "ANALYSIS RESULTS:\n"
                f"ATS Score: {analysis.get('ats_score', 'N/A')}%\n"
                f"Missing Skills: {', '.join(analysis.get('missing_skills', [])[:5])}\n\n"
            )

        prompt += (
            f"USER QUESTION: {user_message}\n\n"
            "Provide a helpful, specific response focusing on their actual resume content. "
            "Include examples when possible."
        )
        return prompt

    def _call_claude(self, prompt: str) -> str:
        """Call Claude API."""
        if not self.api_key:
            return "Please configure Claude API key in the sidebar"

        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            response = requests.post(
                self.api_urls["claude"],
                headers=self._get_headers(),
                json=data,
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()["content"][0]["text"]
            return f"API Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error calling Claude API: {str(e)}"

    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        if not self.api_key:
            return "Please configure OpenAI API key in the sidebar"

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.7,
        }

        try:
            response = requests.post(
                self.api_urls["openai"],
                headers=self._get_headers(),
                json=data,
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            return f"API Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"

    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API."""
        if not self.api_key:
            return "Please configure Gemini API key in the sidebar"

        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1000,
                "topP": 0.95,
                "topK": 40,
            },
        }

        last_error = None
        for model_name in self.gemini_models:
            url = f"{self.api_urls['gemini']}/{model_name}:generateContent?key={self.api_key}"
            try:
                response = requests.post(
                    url,
                    headers=self._get_headers(),
                    json=data,
                    timeout=30,
                )
                if response.status_code == 200:
                    result = response.json()
                    candidates = result.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and parts[0].get("text"):
                            return parts[0]["text"]
                    last_error = "No response generated from Gemini"
                    continue

                try:
                    error_payload = response.json()
                    error_message = error_payload.get("error", {}).get("message", "")
                    error_reason = (
                        error_payload.get("error", {})
                        .get("details", [{}])[0]
                        .get("reason", "")
                    )
                except Exception:
                    error_message = ""
                    error_reason = ""

                if response.status_code == 400 and (
                    "API key not valid" in error_message or error_reason == "API_KEY_INVALID"
                ):
                    return (
                        "Gemini API key is invalid. Please replace `GEMINI_API_KEY` in `.env` "
                        "with a real key from Google AI Studio."
                    )

                last_error = f"API Error: {response.status_code} - {response.text}"
            except Exception as e:
                last_error = f"Error calling Gemini API: {str(e)}"

        return last_error or "Error calling Gemini API"

    def get_resume_feedback(self, context: Dict) -> str:
        """Get general feedback on resume."""
        if not self.api_key:
            return self._get_mock_feedback(context)

        try:
            prompt = self._build_prompt(context)
            if self.provider == "claude":
                return self._call_claude(prompt)
            if self.provider == "openai":
                return self._call_openai(prompt)
            if self.provider == "gemini":
                return self._call_gemini(prompt)
            return self._get_mock_feedback(context)
        except Exception as e:
            return f"Error getting AI feedback: {str(e)}\n\n{self._get_mock_feedback(context)}"

    def chat_with_resume(self, user_message: str, context: Dict) -> str:
        """Chat interaction with resume context."""
        if not self.api_key:
            return self._get_mock_chat_response(user_message, context)

        try:
            prompt = self._build_chat_prompt(user_message, context)
            if self.provider == "claude":
                return self._call_claude(prompt)
            if self.provider == "openai":
                return self._call_openai(prompt)
            if self.provider == "gemini":
                return self._call_gemini(prompt)
            return self._get_mock_chat_response(user_message, context)
        except Exception as e:
            return f"Error: {str(e)}\n\n{self._get_mock_chat_response(user_message, context)}"

    def _get_mock_feedback(self, context: Dict) -> str:
        """Generate mock feedback for demo purposes."""
        job_role = context.get("job_role", "the position")
        ats_score = context.get("ats_score", 65)
        missing_skills = context.get("missing_skills", [])[:3]

        return f"""
### Overall Assessment

Your resume has an ATS score of **{ats_score}%** for {job_role}. Here's my detailed analysis:

### What's Working Well

1. Good skill foundation
2. Clear structure
3. Relevant experience

### Top Priorities for Improvement

1. Add these key skills: {', '.join(missing_skills) if missing_skills else 'industry-standard tools'}
2. Strengthen achievements with metrics
3. Optimize section headings and keywords

Would you like specific help with any section of your resume?
"""

    def _get_mock_chat_response(self, user_message: str, context: Dict) -> str:
        """Generate mock chat response for demo."""
        user_lower = user_message.lower()

        if any(word in user_lower for word in ["skill", "add", "missing"]):
            missing = context.get("analysis_results", {}).get("missing_skills", [])
            if missing:
                return (
                    "Based on your resume analysis, here are the key skills you should add:\n\n"
                    f"- {', '.join(missing[:3])}\n\n"
                    "You can build small projects and add them to your resume while learning."
                )
            return "Your skills section already looks decent. Group skills by category and keep it role-specific."

        if any(word in user_lower for word in ["experience", "bullet", "verb"]):
            return (
                "Use this pattern for stronger bullet points:\n\n"
                "Action Verb + Task + Result\n\n"
                "Example: Optimized database queries, reducing dashboard load time by 40%."
            )

        if any(word in user_lower for word in ["ats", "score", "improve"]):
            ats_score = context.get("analysis_results", {}).get("ats_score", 65)
            return (
                f"To improve your ATS score from {ats_score}%:\n\n"
                "1. Add exact keywords from the target role\n"
                "2. Include more measurable achievements\n"
                "3. Use standard section headings\n"
                "4. Expand your skills section with relevant tools"
            )

        return (
            "I can help rewrite bullet points, improve ATS keywords, tailor your resume "
            "for a role, or suggest better project descriptions."
        )
