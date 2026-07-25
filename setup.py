from setuptools import setup, find_packages

setup(
    name="fastapi-ci-cd",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "sqlalchemy==2.0.23",
        "pydantic==2.5.0",
        "python-dotenv==1.0.0",
    ],
)