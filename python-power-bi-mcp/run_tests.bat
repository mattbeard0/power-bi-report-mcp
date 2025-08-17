@echo off
REM Power BI MCP Test Runner for Windows
REM Usage: run_tests.bat [cleanup_option] [additional_args]

setlocal enabledelayedexpansion

REM Default cleanup option
set CLEANUP_OPTION=clean

REM Check if cleanup option was provided
if not "%1"=="" (
    if "%1"=="clean" (
        set CLEANUP_OPTION=clean
        shift
    ) else if "%1"=="clean-failures" (
        set CLEANUP_OPTION=clean-failures
        shift
    ) else if "%1"=="keep" (
        set CLEANUP_OPTION=keep
        shift
    ) else (
        echo Invalid cleanup option: %1
        echo Valid options: clean, clean-failures, keep
        exit /b 1
    )
)

echo Running Power BI MCP tests with cleanup option: %CLEANUP_OPTION%
echo.

REM Build the command
set CMD=python run_tests.py --cleanup-option "%CLEANUP_OPTION%"

REM Add remaining arguments
:loop
if not "%1"=="" (
    set CMD=!CMD! %1
    shift
    goto loop
)

REM Run the tests
echo Command: !CMD!
echo.
!CMD!

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Tests completed successfully!
) else (
    echo.
    echo Tests failed with exit code: %ERRORLEVEL%
)

endlocal
