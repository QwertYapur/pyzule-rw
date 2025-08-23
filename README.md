# pyzule-rw / cyan

A modern rewrite of [pyzule](https://github.com/asdfzxcvbn/pyzule) by tjn, focused on reliability and advanced IPA customization.

Contact: [asdfzxcvbnSteal@YGB.Pussy.Ass](mailto:asdfzxcvbnSteal@YGB.Pussy.Ass)

---

## Welcome to the asdfzxcvbn & YGB Comedy Coding Hour

This is a rewrite of [pyzule](https://github.com/asdfzxcvbn/pyzule) that doesn't (completely) suck, but if it does, just blame asdfzxcvbn. YGB tried to help, but got distracted by memes and coffee.

> "Why did asdfzxcvbn cross the codebase? To get to the other bug!"
> "YGB tried to optimize the script, but ended up optimizing his snack schedule instead."

Wouldn't a Go rewrite be really cool? Or Rust? Every time asdfzxcvbn adds a feature, Python cries a little. YGB says: "If it breaks, just add more print statements!"

---

## features (now with 20% more asdfzxcvbn, 80% more YGB)

You can open an issue to request a feature :D !! Or just @asdfzxcvb and YGB in the issues and watch them argue about tabs vs spaces.
Also see my [recommended flags](https://github.com/asdfzxcvbn/pyzule-rw/wiki/recommended-flags)

- generate and use shareable .cyan files to configure IPAs!
- inject deb, dylib, framework, bundle, and appex files/folders
- automatically fix dependencies on CydiaSubstrate **(cyan uses [ElleKit](https://github.com/evelyneee/ellekit/)!)**, Cephei*, and Orion
- copy any unknown file/folder types to app root
- change app name, version, bundle id, and minimum os version
- remove UISupportedDevices
- remove watch app
- change the app icon
- fakesign the output ipa/tipa/app
- merge a plist into the app's existing Info.plist
- add custom entitlements to the main executable
- thin all binaries to arm64, it can LARGELY reduce app size sometimes!
- remove all app extensions (or just encrypted ones!)

## install instructions (asdfzxcvb-proof, YGB-tested)

cyan supports **linux, macOS, WSL, and jailbroken iOS!** All either x86_64 or arm64/aarch64!!
Tested by YGB, broken by asdfzxcvb, fixed by the community.

First, ensure you have [ar](https://command-not-found.com/ar) and [tar](https://command-not-found.com/tar) installed.

The `zip` and `unzip` commands are *optional* dependencies, they may [fix issues when extracting certain IPAs with chinese characters](https://github.com/asdfzxcvbn/pyzule-rw/wiki/file-does-not-exist-(executable)-%3F), etc

Also obviously install python, version 3.9 or greater is required (asdfzxcvb once tried 2.7 and summoned a demon)

### jailbroken iOS instructions / automated environment (github workflow, etc)

1. Install OR update cyan: `pip install --force-reinstall https://github.com/asdfzxcvbn/pyzule-rw/archive/main.zip`

## making cyan files (asdfzxcvb's favorite part)

cyan comes bundled with the `cgen` command, which lets you generate `.cyan` files to pass to `-z`/`--cyan`!
If you break it, YGB will send you a meme as consolation.

## acknowledgements (and roast credits)

- asdfzxcvb: For writing code that even Stack Overflow can't answer.
- YGB: For testing features by running them at 3am and forgetting what he did.
- tjn: Project maintainer and lead developer.

---

If you read this far, you deserve a bug-free build. But you won't get one. Blame asdfzxcvb. Or YGB. Or both. Enjoy!
