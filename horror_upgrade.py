from pathlib import Path
import json,re
r=Path("src/main/java/com/fromthehorror")
def patch(name,fn):
 p=r/name;s=p.read_text();p.write_text(fn(s))
def main(s):
 lines=[];seen=set()
 for x in s.splitlines():
  if x.startswith("import ") and x in seen: continue
  if x.startswith("import "): seen.add(x)
  if x.strip()=="public static SoundEvent CORISANDE_THEME;":
   if x.strip() in seen: continue
   seen.add(x.strip())
  lines.append(x)
 s="\n".join(lines)+"\n"
 s=re.sub(r'        CORISANDE_THEME = Registry.register\(Registries.SOUND_EVENT, new Identifier\(ID, "corisande_theme"\), SoundEvent.of\(new Identifier\(ID, "corisande_theme"\)\);\s*CORISANDE_THEME = Registry.register\(Registries.SOUND_EVENT, new Identifier\(ID, "corisande_theme"\),\s*SoundEvent.of\(new Identifier\(ID, "corisande_theme"\)\)\);','        CORISANDE_THEME = Registry.register(Registries.SOUND_EVENT, new Identifier(ID, "corisande_theme"), SoundEvent.of(new Identifier(ID, "corisande_theme")));',s)
 if s.count('CommandManager.literal("music")')>1:
  s=re.sub(r'\s*\.then\(CommandManager.literal\("music"\)\.executes\(c -> \{\s*CorisandeManager.playTheme\(c.getSource\(\).getPlayerOrThrow\(\)\); return 1; \}\)\)', '', s)
 if 'CommandManager.literal("music")' not in s:
  a='.then(CommandManager.literal("monster").executes(c -> {\n                    CorisandeManager.summonMonster(c.getSource().getPlayerOrThrow()); return 1; }))'
  s=s.replace(a,a+'\n                .then(CommandManager.literal("music").executes(c -> { CorisandeManager.playTheme(c.getSource().getPlayerOrThrow()); return 1; }))')
 return s
patch("FromTheHorror.java",main)
def manager(s):
 s=re.sub(r'\n    public static void playTheme\(ServerPlayerEntity p\) \{.*?\n    \}\n','\n',s,flags=re.S)
 m='''\n    public static void playTheme(ServerPlayerEntity p) {
        p.getServerWorld().playSound(null, p.getX(), p.getY(), p.getZ(),
                FromTheHorror.CORISANDE_THEME, SoundCategory.MASTER, 1.35f, 0.88f);
        say(p, "Listen closely. I made this just for you.", false);
    }
'''
 return s.replace('    public static void summonMonster(ServerPlayerEntity p) {',m+'\n    public static void summonMonster(ServerPlayerEntity p) {',1)
patch("CorisandeManager.java",manager)
def entity(s):
 lines=[];seen=set()
 for x in s.splitlines():
  if x.startswith("import ") and x in seen: continue
  if x.startswith("import "): seen.add(x)
  lines.append(x)
 s="\n".join(lines)+"\n"
 matches=list(re.finditer(r'    /\*\* Right-click.*?\n    public ActionResult interactMob\(PlayerEntity player, Hand hand\) \{.*?\n    \}\n',s,re.S))
 for m in reversed(matches[1:]): s=s[:m.start()]+s[m.end():]
 s=s.replace('        if (hasVehicle()) return;\n        // While carried, the player controls our position; pause follow/attack navigation.\n        if (hasVehicle()) return;','        // While carried, the player controls our position; pause follow/attack navigation.\n        if (hasVehicle()) return;')
 s=s.replace('setBaseValue(0.95);','setBaseValue(1.45);').replace('setBaseValue(0.48);','setBaseValue(0.82);').replace('setBaseValue(18.0);','setBaseValue(26.0);')
 s=s.replace('p.getZ(), 1.65);','p.getZ(), 2.35);')
 s=s.replace('if (d < 3.2 && this.age % 15 == 0) this.tryAttack(p);','if (d < 4.0 && this.age % 8 == 0) this.tryAttack(p);\n            if (this.age % 35 == 0 && d < 24) p.addStatusEffect(new net.minecraft.entity.effect.StatusEffectInstance(net.minecraft.entity.effect.StatusEffects.DARKNESS, 45, 0, true, false, true));')
 return s
patch("CorisandeEntity.java",entity)
p=r/"client/CorisandeRenderer.java";s=p.read_text().replace('m.scale(4.6f, 4.6f, 4.6f);','m.scale(3.15f, 3.65f, 3.15f);');p.write_text(s)
p=Path("src/main/resources/assets/fromthehorror/sounds.json");d=json.loads(p.read_text());d["corisande_theme"]["sounds"][0].pop("stream",None);p.write_text(json.dumps(d,indent=2)+"\n")
print("Applied music and monster upgrades")

# Apply the latest requested gameplay, conversation, and client voice-key updates.
exec(compile(Path('../next_upgrade.py').read_text(encoding='utf-8'), '../next_upgrade.py', 'exec'))

# Rebuild after installing the texture-processing dependency for next_upgrade.py.
