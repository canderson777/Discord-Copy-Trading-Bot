# Contributing to Discord Copy Trader Bot

Thank you for your interest in contributing! Here's how you can help improve the project.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature/fix
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## 🛠️ Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/discord-copy-trader-bot.git
cd discord-copy-trader-bot

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env_example.txt .env
# Fill in your test configuration

# Run tests
python test_config.py
python test_signal_parsing.py
python test_multiline_signals.py
```

## 📝 Code Style

- Use descriptive variable and function names
- Add comments for complex logic
- Follow PEP 8 style guidelines
- Include docstrings for functions

## 🧪 Testing

Before submitting:

1. **Test signal parsing**: `python test_signal_parsing.py`
2. **Test configuration**: `python test_config.py`
3. **Test in Discord**: Verify signals are detected correctly
4. **Check logs**: Ensure no errors in console output

## 🎯 Areas for Contribution

### 🔍 Signal Detection
- Add support for new signal formats
- Improve parsing accuracy
- Handle edge cases

### 🛡️ Security & Safety
- Enhance input validation
- Improve error handling
- Add rate limiting

### 📊 Features
- Additional trading platforms
- Portfolio management
- Performance analytics
- Web dashboard

### 📚 Documentation
- Improve setup guides
- Add troubleshooting sections
- Create video tutorials

## 🐛 Bug Reports

When reporting bugs, include:

1. **Environment**: OS, Python version, dependencies
2. **Steps to reproduce**: Clear, numbered steps
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Logs**: Relevant error messages or logs
6. **Signal format**: If related to signal detection

## ✨ Feature Requests

For new features:

1. **Use case**: Why is this feature needed?
2. **Description**: Clear explanation of the feature
3. **Examples**: Show how it would work
4. **Alternatives**: Other ways to achieve the same goal

## 🔒 Security

**Never include sensitive data in PRs:**
- Private keys
- API tokens
- Personal Discord IDs
- Real trading data

Use placeholder values or environment variables.

## 📋 Pull Request Process

1. **Clear title**: Summarize the change
2. **Description**: Explain what and why
3. **Testing**: Show that you've tested the changes
4. **Documentation**: Update docs if needed
5. **Commits**: Use clear, descriptive commit messages

### PR Template
```
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] Tested signal parsing
- [ ] Tested Discord integration
- [ ] No errors in logs

## Screenshots (if applicable)
Add screenshots of Discord interactions

## Additional Notes
Any other relevant information
```

## 📞 Getting Help

- **Discord**: Join our community server
- **Issues**: Create a GitHub issue
- **Discussions**: Use GitHub Discussions for questions

## 🎉 Recognition

Contributors will be:
- Listed in the README
- Mentioned in release notes
- Invited to the contributors team

Thank you for helping make this project better! 🚀
