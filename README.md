
a rewrite of [pyzule](https://github.com/asdfzxcvbn/pyzule) that doesn't (completely) suck !!

# pyzule-rw / cyan

Contact: ZxSteal@YGB.Pussy.Ass

---

## Welcome to the Zxc & YGB Comedy Coding Hour!

This is a rewrite of [pyzule](https://github.com/asdfzxcvbn/pyzule) that doesn't (completely) suck, but if it does, just blame Zxc. YGB tried to help, but got distracted by memes and coffee.

> "Why did Zxc cross the codebase? To get to the other bug!"

> "YGB tried to optimize the script, but ended up optimizing his snack schedule instead."

Wouldn't a Go rewrite be really cool? Or Rust? Every time Zxc adds a feature, Python cries a little. YGB says: "If it breaks, just add more print statements!"

---


## features (now with 20% more Zxc, 80% more YGB)


You can open an issue to request a feature :D !! Or just @Zxc and YGB in the issues and watch them argue about tabs vs spaces.
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


## install instructions (Zxc-proof, YGB-tested)


cyan supports **linux, macOS, WSL, and jailbroken iOS!** All either x86_64 or arm64/aarch64!!
Tested by YGB, broken by Zxc, fixed by the community.

first, make sure you have [ar](https://command-not-found.com/ar) and [tar](https://command-not-found.com/tar) installed


also obviously install python, version 3.9 or greater is required (Zxc once tried 2.7 and summoned a demon)

the `zip` and `unzip` commands are *optional* dependencies, they may [fix issues when extracting certain IPAs with chinese characters](https://github.com/asdfzxcvbn/pyzule-rw/wiki/file-does-not-exist-(executable)-%3F), etc

<details>
<summary><b>linux/WSL/macOS instructions</b></summary>
<br/>
<ol>
  <li>install <a href="https://github.com/pypa/pipx?tab=readme-ov-file#install-pipx">pipx</a></li>
  <li>install OR update cyan: <code>pipx install --force https://github.com/asdfzxcvbn/pyzule-rw/archive/main.zip</code></li>
  <li><b>if you want to inject dylibs ON AARCH64 LINUX</b>: <code>pipx inject cyan lief</code></li>
  <li><b>if you want to change app icons (iOS NOT supported)</b>: <code>pipx inject cyan Pillow</code></li>
</ol>
</details>

<details>
<summary><b>jailbroken iOS instructions / automated environment (github workflow, etc)</b></summary>
<br/>
<ol>
  <li>install OR update cyan: <code>pip install --force-reinstall https://github.com/asdfzxcvbn/pyzule-rw/archive/main.zip</code></li>
</ol>
</details>


## making cyan files (Zxc's favorite part)


cyan comes bundled with the `cgen` command, which lets you generate `.cyan` files to pass to `-z`/`--cyan`!
If you break it, YGB will send you a meme as consolation.


## acknowledgements (and roast credits)

- Zxc: For writing code that even Stack Overflow can't answer.
- YGB: For testing features by running them at 3am and forgetting what he did.


- [Al4ise](https://github.com/Al4ise) for the original [Azule](https://github.com/Al4ise/Azule)
- [lief-project](https://github.com/lief-project) for [LIEF](https://github.com/lief-project/LIEF)
- [tyilo](https://github.com/tyilo) for [insert_dylib](https://github.com/tyilo/insert_dylib/) (macOS/iOS)
- [LeanVel](https://github.com/LeanVel) for [insert_dylib](https://github.com/LeanVel/insert_dylib) (linux)

---

If you read this far, you deserve a bug-free build. But you won't get one. Blame Zxc. Or YGB. Or both. Enjoy!

