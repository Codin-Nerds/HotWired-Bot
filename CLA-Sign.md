Sign the CLA
=============

This page is the step-by-step guide to signing the HotWired-Bot Contributor License Agreement. It's easy and pretty painless!

1. First and foremost, read [the current version of the CLA](cla.md).

2. Make an account on [GitHub](https://github.com/) if you don't already have one.

3. File a pull request on this repository as [outlined below](#filing-the-pull-request).

4. Wait for a team member to merge your pull request.

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

Filing the Pull Request
-----------------------

If you don't yet know how to file a pull request, read [GitHub's
document about it](https://help.github.com/articles/using-pull-requests).

Make your pull request be the addition of a single file to the
[contributors](contributors) directory of this project. Name the file
with the same name as your GitHub userid, with `.md` appended to the
end. For example, for the user `m0`, the full path to the file
would be `contributors/m0.md`.

Put the following in the file:

```txt
[date]

I hereby agree to the terms of the HotWired-Bot Contributor License Agreement, version 1.0, with MD5 checksum
6ac5db65cfe106ebb3b4f567bfab337d.

I furthermore declare that I am authorized and able to make this
agreement and sign this declaration.

Signed,

[your name]
https://github.com/[your github userid]
```

Replace the bracketed text as follows:

* `[date]` with today's date, in the unambiguous numeric form `YYYY-MM-DD`.
* `[your name]` with your name (can be digital nickname).
* `[your github userid]` with your GitHub userid.

You can confirm the MD5 checksum of the CLA by running the md5sum program over `CLA.md`:

```txt
md5sum cla.md
6ac5db65cfe106ebb3b4f567bfab337d  CLA.md
```

If the output is different from above, do not sign the CLA and let us know.

That's it!
