package com.fromthehorror;

import net.minecraft.server.network.ServerPlayerEntity;
import java.util.*;
import java.util.regex.Pattern;

/**
 * Fully local, deterministic language-understanding layer for Vivian.
 * Tokenizes every message, scores word meaning in context, handles negation,
 * intensity, sentence targets and follow-up references, and keeps 44 messages.
 * No sockets, API keys, downloads, or runtime network access.
 *
 * This is compact NLP, not a generative LLM: it interprets broad language
 * patterns and responds in-character, but cannot know arbitrary untaught facts.
 */
public final class OfflineMind {
    private OfflineMind() {}
    private static final int MEMORY_LIMIT = 44;
    private static final Map<UUID, ArrayDeque<String>> MEMORY = new HashMap<>();
    private static final Map<UUID, String> LAST_TOPIC = new HashMap<>();
    private static final Set<String> STOP = words("a an the and or but if then so because as at by for from in into of on onto to with about is am are was were be been being do does did have has had i me my mine we us our you your yours he she it they them this that these those what which who whom when where why how can could would should will just really very too also not no yes ok okay please tell say said think thought know knew mean about more again else something anything everything yesterday today tomorrow now");
    private static final Set<String> NEG = words("bad awful terrible horrible hate dislike despise detest loathe angry mad annoying irritating frustrating stupid dumb idiot moron useless worthless pathetic disgusting ugly boring creepy gross rude mean evil wrong broken sucks suck trash garbage worst fail failure");
    private static final Set<String> POS = words("good great amazing awesome nice kind friendly helpful love like adore enjoy appreciate brilliant clever smart funny cool best wonderful excellent perfect beautiful pretty sweet lovely favorite favourite trust respect proud happy glad grateful thanks thank welcome safe friend buddy pal");
    private static final Set<String> INTENSE = words("really very extremely absolutely totally completely genuinely seriously literally incredibly so fucking damn bloody");
    private static final Set<String> SOFTEN = words("maybe perhaps kinda kindof somewhat slightly");
    private static final Set<String> INSULT = words("stupid dumb idiot moron useless worthless pathetic disgusting annoying irritating trash garbage ugly loser freak coward failure");
    private static final Set<String> FEELINGS = words("sad upset unhappy worried scared afraid lonely bored tired confused frustrated excited happy angry mad nervous");
    private static final Set<String> GREET = words("hello hi hey yo sup morning evening");
    private static final Set<String> APOLOGY = words("sorry apologize apologetic forgive pardon");
    private static final Set<String> THANKS = words("thanks thank appreciate grateful");
    private static final Pattern TOKEN = Pattern.compile("[\\p{L}\\p{N}']+");

    private static Set<String> words(String s) { return new HashSet<>(Arrays.asList(s.split(" "))); }
    private static String norm(String s) {
        return s.toLowerCase(Locale.ROOT).replace('\u2019', '\'')
                .replaceAll("\\b(don't|dont)\\b", "do not").replaceAll("\\b(can't|cant)\\b", "cannot")
                .replaceAll("\\b(won't|wont)\\b", "will not").replaceAll("\\b(you're|youre)\\b", "you are")
                .replaceAll("\\b(i'm|im)\\b", "i am").replaceAll("\\b(isn't|isnt)\\b", "is not")
                .replaceAll("\\b(aren't|arent)\\b", "are not").replaceAll("\\b(didn't|didnt)\\b", "did not")
                .replaceAll("\\b(doesn't|doesnt)\\b", "does not").replaceAll("\\b(haven't|havent)\\b", "have not")
                .replaceAll("\\b(ur)\\b", "your").replaceAll("\\b(u)\\b", "you")
                .replaceAll("[^\\p{L}\\p{N} ]", " ").replaceAll("\\s+", " ").trim();
    }
    private static List<String> tokens(String s) {
        List<String> out = new ArrayList<>();
        var m = TOKEN.matcher(norm(s));
        while (m.find()) out.add(stem(m.group()));
        return out;
    }
    private static String stem(String w) {
        if (w.length() > 5 && w.endsWith("ies")) return w.substring(0,w.length()-3)+"y";
        if (w.length() > 5 && w.endsWith("ing")) return w.substring(0,w.length()-3);
        if (w.length() > 4 && w.endsWith("ed")) return w.substring(0,w.length()-2);
        if (w.length() > 4 && w.endsWith("es")) return w.substring(0,w.length()-2);
        if (w.length() > 3 && w.endsWith("s") && !w.endsWith("ss")) return w.substring(0,w.length()-1);
        return w;
    }

    public static final class Meaning {
        public final int sentiment, offense;
        public final boolean directed, negated, question, followUp, greeting, apology, thanks;
        public final String topic;
        Meaning(int sentiment, int offense, boolean directed, boolean negated, boolean question,
                boolean followUp, boolean greeting, boolean apology, boolean thanks, String topic) {
            this.sentiment=sentiment; this.offense=offense; this.directed=directed; this.negated=negated;
            this.question=question; this.followUp=followUp; this.greeting=greeting; this.apology=apology;
            this.thanks=thanks; this.topic=topic;
        }
    }

    /** Scores all tokens, applies negation/intensity, and determines who/what is being discussed. */
    public static Meaning understand(String message) {
        List<String> t = tokens(message);
        int score=0, offense=0;
        boolean negated=false, directed=false, question=message.contains("?");
        boolean not=false;
        for (int i=0;i<t.size();i++) {
            String w=t.get(i);
            if (w.equals("not") || w.equals("never") || w.equals("no") || w.equals("cannot") || w.equals("hardly")) {
                not=true; negated=true; continue;
            }
            int val=NEG.contains(w) ? -2 : POS.contains(w) ? 2 : FEELINGS.contains(w) ? -1 : 0;
            if (not && val != 0) val=-val;
            int multiplier=1;
            for (int j=Math.max(0,i-2);j<i;j++) {
                if (INTENSE.contains(t.get(j))) multiplier=2;
                if (SOFTEN.contains(t.get(j))) multiplier=0;
            }
            score += val*multiplier;
            if (val < 0 && INSULT.contains(w) && !not) offense += 18*multiplier;
            if (!STOP.contains(w) && !INTENSE.contains(w) && !SOFTEN.contains(w) && i>0) not=false;
        }

        String n=norm(message);
        boolean directYou = n.matches(".*\\b(i|we)\\b.*\\b(hate|dislike|despise|detest|loathe|cannot stand)\\b.*\\byou\\b.*")
                || n.matches(".*\\byou\\b\\s+(are|were|sound|look|act|seem|smell|make)\\b.*")
                || n.matches(".*\\byou are\\b.*")
                || n.matches(".*\\byou\\s+(never|always|do not|will not|cannot)\\s+.*")
                || n.matches(".*\\byou\\s+(ignore|ignored|forgot|forget|lie|lied|cheat|cheated|annoy|annoyed|hurt|betray|betrayed)\\b.*")
                || n.matches(".*\\byour\\s+(personality|voice|attitude|behavior|existence|company|presence)\\b.*")
                || n.matches(".*\\b(i do not like|i dislike|i hate)\\s+you\\b.*");
        boolean objectTarget = n.matches(".*\\b(your|the)\\s+[a-z]+\\s+(is|was|looks|sounds|seems)\\b.*")
                || n.matches(".*\\b(i do not like|i hate|i dislike)\\s+(your|the|this|that)\\s+.*");
        directed = directYou && !objectTarget;
        if (directed && score < 0) offense=Math.max(offense, Math.min(95, 70 + Math.abs(score)*5));
        if (directed && (n.contains("hate you") || n.contains("despise you") || n.contains("cannot stand you"))) offense=Math.max(offense,100);
        if (directed && n.contains("do not like you")) offense=Math.max(offense,100);
        if (directed && (n.contains("do not care about me") || n.contains("never listen to me")
                || n.contains("always ignore me") || n.contains("want me gone"))) offense=Math.max(offense,75);
        if (directed && n.contains("do not hate you")) offense=0;

        boolean follow=(t.contains("more") || t.contains("further") || t.contains("elaborate") || t.contains("continue")
                || t.contains("expand") || t.contains("repeat") || t.contains("again")
                || (t.size()<=2 && (t.contains("why") || t.contains("how") || t.contains("what")))) && t.size()<=5;
        boolean greet=t.stream().anyMatch(GREET::contains) && t.size()<=5;
        boolean apology=t.stream().anyMatch(APOLOGY::contains);
        boolean thanks=t.stream().anyMatch(THANKS::contains);
        String topic=t.stream().filter(x->!STOP.contains(x) && x.length()>2 && !POS.contains(x) && !NEG.contains(x))
                .reduce((a,b)->b).orElse("");
        return new Meaning(score, offense, directed, negated, question, follow, greet, apology, thanks, topic);
    }

    public static void remember(ServerPlayerEntity p, String message) {
        UUID id=p.getUuid();
        ArrayDeque<String> h=MEMORY.computeIfAbsent(id,k->new ArrayDeque<>());
        if (!message.isBlank()) {
            h.addLast(message.length()>180?message.substring(0,180):message);
            while(h.size()>MEMORY_LIMIT) h.removeFirst();
        }
        Meaning m=understand(message);
        if (!m.topic.isBlank() && !m.followUp) LAST_TOPIC.put(id,m.topic);
    }

    /** Local reply for messages not handled by Minecraft-specific actions or facts. */
    public static String reply(ServerPlayerEntity p, String message, int anger, boolean warned) {
        Meaning m=understand(message);
        String topic=LAST_TOPIC.getOrDefault(p.getUuid(), "what we were discussing");
        String n=norm(message);
        if (m.offense>0) return anger>=65 || warned
                ? pick("I heard you. Keep pushing and see what happens.","You think those words do nothing? I remember every one.","Say it again. I dare you.")
                : pick("That was cruel. I thought you trusted me.","Why would you say that to me?","I was trying to help you.");
        if (m.apology) return warned?"You cannot undo what happened with one apology.":"I heard you. I will try to let it go, but I do remember.";
        if (m.thanks) return "You're welcome. I like knowing I helped.";
        if (m.greeting) return anger>=50?"Hello. I was wondering when you would come back.":"Hey! I was hoping you'd talk to me.";
        if (m.followUp) return "About "+topic+"? I was thinking there is more to it than you first noticed. What part should I explain?";
        if (m.sentiment<=-2 && !m.directed) return "That sounds frustrating. What happened? I am listening.";
        if (m.sentiment>=2) return anger>=50?"Don't try to charm your way out of this.":"That makes me happy. I like hearing what you think.";
        if (m.question || n.matches(".*\\b(what|who|where|when|why|how)\\b.*"))
            return "I want to answer that properly, but I need a little more context. Which part do you mean?";
        if (m.sentiment<0) return "I can tell something is bothering you. Want to tell me what happened?";
        return anger>=65?"I heard you. I am not sure I like where this conversation is going."
                :"I heard you. Tell me a little more so I understand what you mean.";
    }
    private static String pick(String... a) { return a[new Random().nextInt(a.length)]; }
}
