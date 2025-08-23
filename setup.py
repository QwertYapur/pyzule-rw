# type: ignore

from setuptools import setup

setup(
  name="cyan",
  version="1.5.0",
  description="Dynamic Telegram privilege menus, user certificate registration, payment system, plugin/appex management, PPQ status, and progress bars.",
  author="zx",
  author_email="moinmedong@protonmail.com",
  packages=["cyan", "cyan.tbhtypes", "cgen"],
  python_requires=">=3.9",
  include_package_data=True,
  entry_points={
    "console_scripts": [
      "cyan=cyan.__main__:main",
      "cgen=cgen.__main__:main"
    ],
  }
)

