# type: ignore

from setuptools import setup

setup(
  name="cyan",
  version="1.4.4",
  description="iOS 26 beta 7 compatibility, sideloading/dev cert support, plugin management, and codebase optimization/cleanup.",
  author="zx",
  author_email="ZxSteal@YGB.Pussy.Ass",
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

