from pathlib import Path
import sys, math
from PIL import Image, ImageDraw, ImageFilter
root=Path(sys.argv[1]); base=root/'src/main/java/com/fromthehorror'
def edit(n,f):
 p=base/n; s=p.read_text(); p.write_text(f(s))
def d(s):
 s=s.replace('240 + R.nextInt(360)','45 + R.nextInt(75)')
 a=s.index('        if (underground) {',s.index('private static void naturalSpawn'))
 b=s.index('\n    }',a)
 s=s[:a]+'''        if (underground) {
            if (roll < 48) spawn(w,p,FromTheHorror.DWELLER,18,32);
            else if (roll < 68) spawn(w,p,FromTheHorror.LURKER,22,36);
            else if (roll < 86) spawn(w,p,FromTheHorror.MIMIC,22,38);
            else if (roll < 96 && nightOrStorm) spawn(w,p,FromTheHorror.MAN,30,44);
            else spawn(w,p,FromTheHorror.STALKER,22,36);
        } else if (nightOrStorm) {
            if (roll < 14) spawn(w,p,FromTheHorror.SCREECHER,28,44);
            else if (roll < 28) spawn(w,p,FromTheHorror.MIMIC,28,44);
            else if (roll < 42) spawn(w,p,FromTheHorror.WATCHER,30,46);
            else if (roll < 54) spawn(w,p,FromTheHorror.MAN,28,42);
            else if (roll < 62) spawn(w,p,FromTheHorror.HOLLOW,28,42);
            else if (roll < 70) spawn(w,p,FromTheHorror.STALKER,28,42);
            else if (roll < 78) spawn(w,p,FromTheHorror.GRINNER,28,42);
            else if (roll < 84) spawn(w,p,FromTheHorror.PALE_ONE,28,42);
            else if (roll < 90) spawn(w,p,FromTheHorror.CRAWLER,28,42);
            else if (roll < 95) spawn(w,p,FromTheHorror.SIREN,28,42);
            else spawn(w,p,FromTheHorror.RAVEN,28,42);
        } else if (roll < 18) spawn(w,p,FromTheHorror.MAN,32,48);''' +s[b:]
 return s
edit('DreadDirector.java',d)
def st(s):
 s=s.replace('public boolean met, turned, dead, warned, greeted, carried;','public boolean met, turned, dead, warned, greeted, carried, cycleInitialized, lastNight;\n    public int completedCycles;')
 s=s.replace('n.putBoolean("carried", carried);','n.putBoolean("carried", carried); n.putBoolean("cycleInitialized", cycleInitialized); n.putBoolean("lastNight", lastNight); n.putInt("completedCycles", completedCycles);')
 s=s.replace('s.carried = n.getBoolean("carried");','s.carried = n.getBoolean("carried"); s.cycleInitialized = n.getBoolean("cycleInitialized"); s.lastNight = n.getBoolean("lastNight"); s.completedCycles = n.getInt("completedCycles");')
 return s
edit('CorisandeState.java',st)
def cm(s):
 s=s.replace('long day=w.getTimeOfDay()/24000L;\n        boolean complete=state.warned && day>=state.madDay+COUNTDOWN_DAYS && w.isNight();','boolean complete=state.warned && state.completedCycles>=COUNTDOWN_DAYS && w.isNight();')
 s=s.replace('long day = w.getTimeOfDay() / 24000L;\n        seconds++;','boolean nightNow=w.isNight();\n        if (!st.cycleInitialized) { st.cycleInitialized=true; st.lastNight=nightNow; st.markDirty(); }\n        else if (!st.lastNight && nightNow) { st.completedCycles++; st.lastNight=true; st.markDirty(); }\n        else if (st.lastNight && !nightNow) { st.lastNight=false; st.markDirty(); }\n        seconds++;')
 s=s.replace('if (st.warned && !st.turned && day >= st.madDay + COUNTDOWN_DAYS && w.isNight()) turnNow(w);','if (st.warned && !st.turned && st.completedCycles>=COUNTDOWN_DAYS && w.isNight()) turnNow(w);')
 s=s.replace('st.anger = 0; st.greed = 0; st.madDay = 0; st.entity = null;','st.anger = 0; st.greed = 0; st.madDay = 0; st.entity = null; st.completedCycles=0; st.cycleInitialized=false; st.lastNight=false;')
 s=s.replace('The third day is over. Day and night, five times. Now you see what I really am.','Three day-to-night cycles have passed. Now you see what I really am.')
 return s
edit('CorisandeManager.java',cm)
def ce(s):
 s=s.replace('carried.getOrCreateNbt().put("CorisandeData",data);','carried.getOrCreateNbt().put("CorisandeData",data);\n            if (getMood() >= 2) carried.getOrCreateNbt().putInt("CustomModelData",1);')
 s=s.replace('''if (getType() == FromTheHorror.CORISANDE_MONSTER) return;''','''if (getType() == FromTheHorror.CORISANDE_MONSTER) { for (ServerPlayerEntity pl : sw.getPlayers()) CorisandeManager.say(pl, "Thank you for removing the darkness inside me", false); return; }''')
 return s
edit('CorisandeEntity.java',ce)
p=base/'NaturalStructures.java'; s=p.read_text()
if 'public static BlockPos nearest' not in s:
 s=s.replace('import java.util.Set;','import java.util.Set;\nimport java.util.List;\nimport java.util.ArrayList;')
 s=s.replace('private static final Set<Long> DONE = new HashSet<>();','private static final Set<Long> DONE = new HashSet<>();\n private static final List<BlockPos> CABINS=new ArrayList<>(), SHRINES=new ArrayList<>();\n public static BlockPos nearest(BlockPos from, boolean cabin){return (cabin?CABINS:SHRINES).stream().min(java.util.Comparator.comparingLong(p->p.getSquaredDistance(from))).orElse(null);}')
 s=s.replace('private static void place(ServerWorld w, BlockPos p, boolean cabin){','private static void place(ServerWorld w, BlockPos p, boolean cabin){\n  (cabin?CABINS:SHRINES).add(p.toImmutable());')
 p.write_text(s)
p=base/'FromTheHorror.java'; s=p.read_text()
if 'literal("fromthehorror")' not in s:
 marker='            dispatcher.register(CommandManager.literal("corisande")'
 s=s.replace(marker,'''            dispatcher.register(CommandManager.literal("locate").then(CommandManager.literal("fromthehorror")
                .then(CommandManager.literal("house").executes(c->{var pl=c.getSource().getPlayerOrThrow(); var pos=NaturalStructures.nearest(pl.getBlockPos(),true); if(pos==null){pl.sendMessage(net.minecraft.text.Text.literal("No house generated this session yet; explore new chunks."),false);return 0;} pl.sendMessage(net.minecraft.text.Text.literal("Nearest FromTheHorror house: "+pos.toShortString()),false);return 1;}))
                .then(CommandManager.literal("shrine").executes(c->{var pl=c.getSource().getPlayerOrThrow(); var pos=NaturalStructures.nearest(pl.getBlockPos(),false); if(pos==null){pl.sendMessage(net.minecraft.text.Text.literal("No shrine generated this session yet; explore new chunks."),false);return 0;} pl.sendMessage(net.minecraft.text.Text.literal("Nearest FromTheHorror shrine: "+pos.toShortString()),false);return 1;}))));
''' + marker)
 s=s.replace('long currentDay = player.getServerWorld().getTimeOfDay() / 24000L;\n                    long remaining = state.warned ? Math.max(0, state.madDay + CorisandeManager.COUNTDOWN_DAYS - currentDay) : -1;','int remaining = state.warned ? Math.max(0, CorisandeManager.COUNTDOWN_DAYS - state.completedCycles) : -1;')
 s=s.replace('The fifth cycle is complete. Corisande will transform when night falls.','Three day-to-night cycles are complete. Corisande will transform when night falls.')
 s=s.replace('full Minecraft day/night cycles remain','day-to-night cycles remain')
 p.write_text(s)
# item icon: illustrated orb instead of the entity UV atlas
asset=root/'src/main/resources/assets/fromthehorror'; tex=asset/'textures/item'; tex.mkdir(parents=True,exist_ok=True)
for angry in (False,True):
 im=Image.new('RGBA',(64,64)); px=im.load()
 for y in range(64):
  for x in range(64):
   d=math.hypot(x-32,y-32)
   if d<=25:
    l=max(0,1-math.hypot(x-23,y-19)/28); t=d/25; px[x,y]=(int(190+55*l-40*t),int(75+95*l-35*t),int(10+20*l),255)
 im=Image.alpha_composite(im.filter(ImageFilter.GaussianBlur(7)),im); dr=ImageDraw.Draw(im); dr.ellipse((14,10,25,20),fill=(255,218,130,180))
 if angry:
  dr.line((19,25,28,29),fill=(55,20,10),width=4); dr.line((36,29,45,25),fill=(55,20,10),width=4); dr.ellipse((22,31,27,37),fill=(25,10,5)); dr.ellipse((37,31,42,37),fill=(25,10,5)); dr.arc((22,39,43,54),200,340,fill=(35,8,5),width=4)
 else:
  dr.ellipse((21,27,27,36),fill=(35,12,4)); dr.ellipse((37,27,43,36),fill=(35,12,4)); dr.arc((22,31,43,49),10,170,fill=(45,12,4),width=3)
 im.save(tex/('corisande_carry_angry.png' if angry else 'corisande_carry.png'))
models=asset/'models/item'
(models/'corisande_carry.json').write_text('{"parent":"minecraft:item/generated","textures":{"layer0":"fromthehorror:item/corisande_carry"},"overrides":[{"predicate":{"custom_model_data":1},"model":"fromthehorror:item/corisande_carry_angry"}]}')
(models/'corisande_carry_angry.json').write_text('{"parent":"minecraft:item/generated","textures":{"layer0":"fromthehorror:item/corisande_carry_angry"}}')
print('feature fixes applied')
