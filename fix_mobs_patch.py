from pathlib import Path
p=Path("finish_mobs.py")
s=p.read_text(encoding="utf-8")
a=s.index("# Remove now-obsolete duplicate branch tail introduced by replacement.")
b=s.index("# Texture variants",a)
p.write_text(s[:a]+s[b:],encoding="utf-8")
print("Removed the redundant second natural-spawn rewrite; the first replacement already leaves a valid disabled legacy branch.")
