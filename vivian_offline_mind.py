from pathlib import Path
import shutil
import re

base = Path('src/main/java/com/fromthehorror')
shutil.copyfile(Path('../OfflineMind.java'), base / 'OfflineMind.java')

brain = base / 'CorisandeBrain.java'
s = brain.read_text(encoding='utf-8')
start = s.index('    /** Returns 100 for a severe personal attack')
end = s.index('\n    public static String reply(', start)
s = s[:start] + '''    /** Semantic offense analysis is handled by the fully local OfflineMind parser. */
    private static int offenseLevel(String s, boolean addressed) {
        OfflineMind.Meaning meaning = OfflineMind.understand(s);
        return meaning.directed ? meaning.offense : 0;
    }
''' + s[end:]
s = s.replace('''        if (any(s, "i love you", "i like you", "i really like you", "best friend", "my friend", "good job", "you are great", "you are awesome", "you are helpful", "you are kind", "you are nice")) return st.warned ? "Careful what you promise me." : "That makes me really happy. You're my favorite.";''', '''        OfflineMind.Meaning meaning = OfflineMind.understand(msg);
        if (meaning.sentiment >= 2 && !meaning.directed && !meaning.negated) return st.warned ? "Careful what you promise me." : "That makes me really happy. You're my favorite.";''')
brain.write_text(s, encoding='utf-8')

manager = base / 'CorisandeManager.java'
s = manager.read_text(encoding='utf-8')
s = s.replace('''        remember(sender, msg);
        String reply = CorisandeBrain.reply(sender, msg.isEmpty() ? "hello" : msg, st, c, w, addressed);''', '''        remember(sender, msg);
        OfflineMind.remember(sender, msg);
        String reply = CorisandeBrain.reply(sender, msg.isEmpty() ? "hello" : msg, st, c, w, addressed);''')
s, count = re.subn(
    r"        boolean wantsAi =.*?        if \(reply != null\) say\(sender, reply, st\.turned \|\| st\.warned\);",
    "        st.markDirty();\n        // Offline-only: never invoke the optional HTTP language-model client.\n        if (CorisandeBrain.fallback && addressed && !msg.isEmpty()) {\n            reply = OfflineMind.reply(sender, msg, st.anger, st.warned);\n        }\n        if (reply != null) say(sender, reply, st.turned || st.warned);",
    s, count=1, flags=re.S)
if count != 1:
    raise SystemExit('Could not replace online AI fallback with offline-only path')
manager.write_text(s, encoding='utf-8')
print('Installed Vivian offline language understanding.')
