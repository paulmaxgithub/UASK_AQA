.PHONY: help install test test-ui test-ai test-security test-smoke test-parallel test-headless test-english test-arabic clean report test-stealth

# Default target
.DEFAULT_GOAL := help

# Python and pytest commands
PYTHON := python3
PYTEST := pytest
PIP := pip

help:
	@echo "U-Ask QA Automation Framework"
	@echo "=============================="
	@echo ""
	@echo "Available commands:"
	@echo "  make install         - Install dependencies and setup environment"
	@echo "  make test            - Run all tests"
	@echo "  make test-smoke      - Run smoke tests (quick)"
	@echo "  make test-ui         - Run UI behavior tests"
	@echo "  make test-ai         - Run AI response validation tests"
	@echo "  make test-security   - Run security tests"
	@echo "  make test-parallel   - Run tests in parallel"
	@echo "  make test-headless   - Run tests in headless mode"
	@echo "  make test-english    - Run tests in English"
	@echo "  make test-arabic     - Run tests in Arabic"
	@echo "  make test-stealth    - Run tests in STEALTH mode (bypass CAPTCHA)"
	@echo "  make test-stealth-headless - Run tests in stealth mode (headless)"
	@echo "  make report          - Run tests and generate HTML report"
	@echo "  make allure-report   - Run tests and generate Allure report"
	@echo "  make allure-serve    - Run tests and open Allure report in browser"
	@echo "  make clean           - Clean temporary files and reports"
	@echo ""

install:
	@echo "Setting up environment..."
	$(PYTHON) -m venv venv || true
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Installing Playwright browsers..."
	playwright install
	@echo ""
	@echo "Installation complete!"
	@echo "Activate virtual environment: source venv/bin/activate"

test:
	@echo "Running all tests..."
	$(PYTEST) -v

test-smoke:
	@echo "Running smoke tests..."
	$(PYTEST) -v -m smoke

test-ui:
	@echo "Running UI tests..."
	$(PYTEST) -v -m ui

test-ai:
	@echo "Running AI response tests..."
	$(PYTEST) -v -m ai_response

test-security:
	@echo "Running security tests..."
	$(PYTEST) -v -m security

test-parallel:
	@echo "Running tests in parallel..."
	$(PYTEST) -v -n 4

test-headless:
	@echo "Running tests in headless mode..."
	$(PYTEST) -v --headless

test-english:
	@echo "Running English tests..."
	$(PYTEST) -v --language=en

test-arabic:
	@echo "Running Arabic tests..."
	$(PYTEST) -v --language=ar

test-stealth:
	@echo "Running tests in STEALTH mode (CAPTCHA bypass)..."
	$(PYTEST) -v --stealth

test-stealth-headless:
	@echo "Running tests in STEALTH mode (headless)..."
	$(PYTEST) -v --stealth --headless

test-stealth-session:
	@echo "Running tests with saved session..."
	$(PYTEST) -v --stealth --session-file saved_session.json

report:
	@echo "Running tests and generating HTML report..."
	$(PYTEST) -v --html=reports/test_report.html --self-contained-html
	@echo ""
	@echo "Report generated: reports/test_report.html"

allure-report:
	@echo "Running tests with Allure reporting..."
	$(PYTEST) -v --alluredir=reports/allure-results
	@echo ""
	@echo "Generating Allure report..."
	allure generate reports/allure-results -o reports/allure-report --clean
	@echo ""
	@echo "Allure report generated: reports/allure-report/index.html"
	@echo "To view: allure open reports/allure-report"

allure-serve:
	@echo "Running tests and serving Allure report..."
	$(PYTEST) -v --alluredir=reports/allure-results
	allure serve reports/allure-results

clean:
	@echo "Cleaning temporary files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/ .tox/ 2>/dev/null || true
	rm -rf reports/*.html reports/logs/*.log 2>/dev/null || true
	rm -rf reports/allure-results reports/allure-report 2>/dev/null || true
	@echo "Clean complete!"
