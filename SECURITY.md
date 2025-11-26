# Security Policy

## Supported Versions

Currently supported versions of AI Computer Automation:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow these steps:

### 1. Do Not Publicly Disclose

**Please do not open a public issue** for security vulnerabilities. This could put users at risk.

### 2. Report Privately

Report security vulnerabilities by:

- **Email**: Send details to the project maintainers
- **GitHub Security Advisory**: Use [GitHub's security advisory feature](https://github.com/treesbeats/ai-computer-automation/security/advisories/new)

### 3. Include Details

Please include:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if you have one)
- Your contact information

### 4. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Varies by severity
  - Critical: Within 7 days
  - High: Within 14 days
  - Medium: Within 30 days
  - Low: Next scheduled release

## Security Best Practices

### For Users

#### API Keys and Secrets

- **Never commit API keys** to version control
- Store API keys in `.env` file (already in `.gitignore`)
- Use environment variables for sensitive configuration
- Rotate API keys regularly
- Use different API keys for development and production

#### Safe Automation

- **Review scripts** before running automation tasks
- Enable `SAFE_MODE=true` in `.env` for additional safety checks
- Use `REQUIRE_CONFIRMATION=true` for sensitive operations
- Test automation in a safe environment first
- Monitor automation tasks for unexpected behavior

#### Dependencies

- Keep dependencies up to date
- Review dependency security advisories
- Use virtual environments
- Run `pip audit` regularly to check for known vulnerabilities

```bash
# Install pip-audit
pip install pip-audit

# Check for vulnerabilities
pip-audit
```

#### System Permissions

- Grant minimal required permissions
- Review automation scripts' required permissions
- On macOS: Only grant Accessibility permissions when needed
- On Windows: Avoid running with administrator privileges unless necessary
- On Linux: Use appropriate user permissions

### For Developers

#### Code Security

- **Input validation**: Validate all user inputs
- **Sanitize data**: Clean data before processing
- **Avoid shell injection**: Use subprocess safely
- **Path traversal**: Validate file paths
- **Rate limiting**: Implement rate limits for API calls

#### Example - Safe Subprocess Usage

```python
# Bad - vulnerable to injection
import os
os.system(f"rm {user_input}")

# Good - safe parameterization
import subprocess
subprocess.run(["rm", user_input], check=True)
```

#### Example - Path Validation

```python
from pathlib import Path

def safe_file_access(user_path: str, base_dir: str) -> Path:
    """Safely resolve and validate file path."""
    base = Path(base_dir).resolve()
    target = (base / user_path).resolve()

    # Ensure target is within base directory
    if not str(target).startswith(str(base)):
        raise ValueError("Path traversal attempt detected")

    return target
```

#### Secure API Integration

- Use official SDK libraries when available
- Validate API responses
- Handle API errors gracefully
- Implement timeout mechanisms
- Log API usage for auditing

```python
import openai
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=30.0,  # Prevent hanging
)

try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=100,  # Limit response size
    )
except openai.APIError as e:
    # Handle API errors
    logger.error(f"API error: {e}")
```

#### Testing Security

- Include security test cases
- Test input validation
- Test authentication/authorization
- Use static analysis tools
- Perform dependency scanning

```bash
# Static analysis
bandit -r src/

# Dependency scanning
safety check
pip-audit
```

## Known Security Considerations

### Computer Vision & Screenshots

- **Privacy**: Screenshots may capture sensitive information
- Configure `SCREENSHOT_DIR` to a secure location
- Implement automatic screenshot cleanup
- Consider encryption for stored screenshots

### GUI Automation

- **Privilege escalation**: GUI automation may interact with privileged applications
- Run automation with minimal privileges
- Validate target applications before interaction
- Implement safety timeouts

### AI API Usage

- **Data privacy**: Be aware of data sent to AI APIs
- Review API provider privacy policies
- Don't send sensitive/confidential data to external APIs
- Consider using local AI models for sensitive data

### Credentials Management

- Never log credentials
- Use credential managers when possible
- Implement credential rotation
- Clear credentials from memory after use

## Security Updates

Security updates will be:

- Announced in release notes
- Tagged with `[SECURITY]` prefix
- Documented in `CHANGELOG.md`
- Posted to GitHub Security Advisories

## Vulnerability Disclosure Policy

We follow responsible disclosure:

1. Report received and acknowledged
2. Vulnerability verified and assessed
3. Fix developed and tested
4. Security advisory prepared
5. Fix released
6. Advisory published (after users have time to update)

## Security Checklist for Contributors

Before submitting code:

- [ ] No hardcoded secrets or API keys
- [ ] Input validation implemented
- [ ] Error handling doesn't leak sensitive info
- [ ] Dependencies are up to date
- [ ] Security-relevant changes are documented
- [ ] Tests include security scenarios
- [ ] Code has been reviewed for common vulnerabilities

## Common Vulnerabilities to Avoid

### Injection Attacks

- Command injection
- Path traversal
- Code injection

### Data Exposure

- Logging sensitive data
- Exposing API keys
- Storing credentials insecurely

### Insufficient Validation

- Missing input validation
- Inadequate type checking
- Improper error handling

## Resources

### Security Tools

- [Bandit](https://bandit.readthedocs.io/) - Python security linter
- [Safety](https://pyup.io/safety/) - Dependency vulnerability scanner
- [pip-audit](https://pypi.org/project/pip-audit/) - Audit Python dependencies
- [Snyk](https://snyk.io/) - Security scanning platform

### Security Guidelines

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [OpenAI Security Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)

## Questions?

For security questions (not vulnerability reports), please:

- Open a discussion on GitHub
- Consult the documentation
- Review existing security advisories

Thank you for helping keep AI Computer Automation secure!
