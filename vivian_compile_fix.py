from pathlib import Path
root=Path("src/main/java/com/fromthehorror")
p=root/"CorisandeManager.java"
s=p.read_text(encoding="utf-8")
s=s.replace("long now = w.getTime();\n        ArrayDeque<Long> times", "long chatTick = w.getTime();\n        ArrayDeque<Long> times", 1)
s=s.replace("times.addLast(now);", "times.addLast(chatTick);", 1)
s=s.replace("now - times.peekFirst() > 60", "chatTick - times.peekFirst() > 60", 1)
s=s.replace("now >= SPAM_COOLDOWN", "chatTick >= SPAM_COOLDOWN", 1)
s=s.replace("SPAM_COOLDOWN.put(sender.getUuid(), now + 60);", "SPAM_COOLDOWN.put(sender.getUuid(), chatTick + 60);", 1)
s=s.replace('" days, " + p.getName().getString()', '" full day-to-night cycles, " + p.getName().getString()', 1)
s=s.replace("Three full Minecraft days must pass", "Three full day-to-night cycles must pass")
p.write_text(s,encoding="utf-8")
b=root/"CorisandeBrain.java"
t=b.read_text(encoding="utf-8").replace("Zero days. It is time.", "Zero cycles. It is time.")
b.write_text(t,encoding="utf-8")
print("Fixed chat timer variable collision and aligned countdown wording to three day-to-night cycles.")
