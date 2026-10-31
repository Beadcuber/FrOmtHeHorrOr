from pathlib import Path
import json
r=Path("src/main/java/com/fromthehorror")
def edit(name,old,new,count=1):
 p=r/name;s=p.read_text()
 if old not in s: raise SystemExit(f"Missing {name}: {old[:90]}")
 p.write_text(s.replace(old,new,count))
edit("CorisandeManager.java","public static final int COUNTDOWN_DAYS = 5;","public static final int COUNTDOWN_DAYS = 3;")
p=r/"CorisandeManager.java";s=p.read_text()
s=s.replace("14-day","3-day").replace("five-day","three-day").replace("Five days","Three days").replace("fifth day","third day").replace("fifth cycle","third cycle").replace("in 5 days","in 3 days")
s=s.replace("import java.util.Random;","import java.util.Random;\nimport java.util.ArrayDeque;\nimport java.util.HashMap;\nimport java.util.Map;\nimport java.util.UUID;")
s=s.replace("    private static final Random R = new Random();","    private static final Random R = new Random();\n    private static final Map<UUID, ArrayDeque<String>> RECENT_CHAT = new HashMap<>();")
s=s.replace("        String reply = CorisandeBrain.reply(sender, msg.isEmpty() ? \"hello\" : msg, st, c, w, addressed);","        remember(sender, msg);\n        String reply = CorisandeBrain.reply(sender, msg.isEmpty() ? \"hello\" : msg, st, c, w, addressed);")
s=s.replace("AiChat.ask(sender, msg, systemPrompt(sender, st, w), r -> {","AiChat.ask(sender, msg, systemPrompt(sender, st, w) + recentContext(sender), r -> {")
anchor="    private static String systemPrompt(ServerPlayerEntity p, CorisandeState st, ServerWorld w) {"
methods="""    private static void remember(ServerPlayerEntity p, String message) {
        ArrayDeque<String> h=RECENT_CHAT.computeIfAbsent(p.getUuid(),k->new ArrayDeque<>());
        if(!message.isBlank()) h.addLast("Player: "+message);
        while(h.size()>12) h.removeFirst();
    }
    private static String recentContext(ServerPlayerEntity p) {
        ArrayDeque<String> h=RECENT_CHAT.get(p.getUuid());
        return h==null||h.isEmpty()?"":" Recent conversation: "+String.join(" | ",h)+". Use this context naturally.";
    }
"""
s=s.replace(anchor,methods+anchor);p.write_text(s)
p=r/"CorisandeManager.java";s=p.read_text()
s=s.replace("    public static void summonMonster(ServerPlayerEntity p) {\n        ServerWorld w = p.getServerWorld();","""    public static void summonMonster(ServerPlayerEntity p) {
        ServerWorld w = p.getServerWorld();
        CorisandeState state=CorisandeState.get(w);
        long day=w.getTimeOfDay()/24000L;
        boolean complete=state.warned && day>=state.madDay+COUNTDOWN_DAYS && w.isNight();
        if(!p.hasPermissionLevel(2) && !complete) {
            say(p,"You cannot call that form early. Three full Minecraft days must pass, and night must fall.",true);
            return;
        }""");p.write_text(s)
p=r/"FromTheHorror.java";s=p.read_text()
s=s.replace('.then(CommandManager.literal("monster").executes(c -> {','.then(CommandManager.literal("monster").requires(src -> src.hasPermissionLevel(2)).executes(c -> {')
s=s.replace('.then(CommandManager.literal("corisande_monster").executes(c -> {','.then(CommandManager.literal("corisande_monster").requires(src -> src.hasPermissionLevel(2)).executes(c -> {');p.write_text(s)
p=r/"CorisandeEntity.java";s=p.read_text()
s=s.replace("import net.minecraft.world.World;","import net.minecraft.world.World;\nimport net.minecraft.world.GameRules;\nimport net.minecraft.block.Blocks;")
s=s.replace("            this.getNavigation().startMovingTo(p.getX(), p.getY() + 1.8, p.getZ(), 2.35);","            this.getNavigation().startMovingTo(p.getX(), p.getY() + 1.8, p.getZ(), 2.35);\n            if (this.age % 5 == 0) breakObstruction((ServerWorld) w, p);")
anchor="    @Override\n    public boolean damage(DamageSource source, float amount) {"
method="""    private void breakObstruction(ServerWorld world, PlayerEntity target) {
        if(!world.getGameRules().getBoolean(GameRules.DO_MOB_GRIEFING)) return;
        net.minecraft.util.math.Vec3d v=target.getPos().subtract(getPos()).normalize();
        BlockPos base=getBlockPos().add((int)Math.round(v.x),0,(int)Math.round(v.z));
        for(int y=0;y<3;y++){
            BlockPos at=base.up(y); var state=world.getBlockState(at);
            if(state.isAir()||state.isOf(Blocks.BEDROCK)||state.isOf(Blocks.BARRIER)||state.isOf(Blocks.END_PORTAL)
                ||state.isOf(Blocks.END_PORTAL_FRAME)||state.getHardness(world,at)<0||world.getBlockEntity(at)!=null) continue;
            if(state.getHardness(world,at)<=8.0f){world.breakBlock(at,true,this);break;}
        }
    }

"""
s=s.replace(anchor,method+anchor);p.write_text(s)
p=r/"DreadDirector.java";s=p.read_text().replace("900 + R.nextInt(900)","240 + R.nextInt(360)").replace("!w.isSkyVisible(pos) && pos.getY() < 56","!w.isSkyVisible(pos) && pos.getY() < 80").replace("if (roll < 42) spawn(w, p, FromTheHorror.DWELLER, 24, 38);","if (roll < 78) spawn(w, p, FromTheHorror.DWELLER, 18, 32)");p.write_text(s)
p=r/"client/CorisandeRenderer.java";s=p.read_text()
s=s.replace("    private static final Identifier[] FACES = new Identifier[5];","    private static final Identifier[] FACES = new Identifier[5];\n    private static final Identifier BLANK = new Identifier(FromTheHorror.ID, \"textures/entity/corisande_blank.png\");")
s=s.replace("    public Identifier getTexture(CorisandeEntity e) {\n        return FACES","    public Identifier getTexture(CorisandeEntity e) {\n        if (e.isHostile()) return BLANK;\n        return FACES");p.write_text(s)
import subprocess
subprocess.run(["sudo","apt-get","install","-y","python3-pil"],check=True)
from PIL import Image
tex=Path("src/main/resources/assets/fromthehorror/textures/entity")
im=Image.open(tex/"corisande_4.png").convert("RGBA");px=im.load()
for y in range(8,24):
 for x in range(8,24):
  rr,gg,bb,aa=px[x,y]
  if aa:
   v=int((rr+gg+bb)/3);px[x,y]=(int(v*.18),int(v*.16),int(v*.18),aa)
im.save(tex/"corisande_blank.png")
p=r/"client/FromTheHorrorClient.java";s=p.read_text()
s=s.replace("import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;","import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;\nimport net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;\nimport net.minecraft.client.option.KeyBinding;\nimport org.lwjgl.glfw.GLFW;")
s=s.replace("    private static boolean voice = true;","    private static boolean voice = true;\n    private static KeyBinding voiceSettingsKey;")
s=s.replace("        // Fog closes in when the Man from the Fog is near.","""        voiceSettingsKey=KeyBindingHelper.registerKeyBinding(new KeyBinding("key.fromthehorror.voice_settings",GLFW.GLFW_KEY_V,"category.fromthehorror"));
        ClientTickEvents.END_CLIENT_TICK.register(client -> { while(voiceSettingsKey.wasPressed()) {
            if(VoiceListener.isOn()){VoiceListener.stop();if(client.player!=null)client.player.sendMessage(Text.literal("[Corisande VC] Microphone OFF. Press V to turn it on."),false);}
            else VoiceListener.start(client,false);
        }});
        // Fog closes in when the Man from the Fog is near.""")
s=s.replace("        // She hears you from the moment you join (Windows). /corilisten off to stop.\n        ClientPlayConnectionEvents.JOIN.register((handler, sender, client) -> VoiceListener.start(client, true));\n","")
p.write_text(s)
lp=Path("src/main/resources/assets/fromthehorror/lang/en_us.json");d=json.loads(lp.read_text());d["key.fromthehorror.voice_settings"]="Toggle Corisande Voice Chat";d["category.fromthehorror"]="FromTheHorror";lp.write_text(json.dumps(d,indent=2)+"\n")
print("Applied 3-day timer, permission-gated summon, blank face, frequent cave encounters, mob-griefing block breaking, recent chat context, and V voice toggle.")
