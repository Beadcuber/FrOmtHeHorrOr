from pathlib import Path
import json

root = Path("src/main/java/com/fromthehorror/client")
voice = root / "VoiceListener.java"
voice.write_text(r'''package com.fromthehorror.client;

import net.minecraft.client.MinecraftClient;
import net.minecraft.text.Text;
import net.minecraft.util.Formatting;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/** Windows speech recognition for Corisande. Starts when a world is joined; V mutes/unmutes it. */
public final class VoiceListener {
    private VoiceListener() {}
    private static volatile Process proc;
    private static volatile boolean ready;
    private static boolean hookAdded;

    private static final String SCRIPT = """
        $ErrorActionPreference = 'Stop'
        try {
          Add-Type -AssemblyName System.Speech
          $engine = New-Object System.Speech.Recognition.SpeechRecognitionEngine
          $engine.SetInputToDefaultAudioDevice()
          $engine.LoadGrammar((New-Object System.Speech.Recognition.DictationGrammar))
          $engine.add_SpeechRecognized({
            param($sender, $eventArgs)
            if ($eventArgs.Result.Confidence -ge 0.55) {
              $recognized = ($eventArgs.Result.Text -replace '[\\r\\n]+', ' ').Trim()
              if ($recognized.Length -gt 0) {
                [Console]::Out.WriteLine('HEARD:' + $recognized)
                [Console]::Out.Flush()
              }
            }
          })
          [Console]::Out.WriteLine('READY')
          [Console]::Out.Flush()
          $engine.RecognizeAsync([System.Speech.Recognition.RecognizeMode]::Multiple)
          while ($true) { Start-Sleep -Milliseconds 250 }
        } catch {
          [Console]::Out.WriteLine('ERROR:' + $_.Exception.Message)
          [Console]::Out.Flush()
        }
        """;

    public static boolean isOn() { return proc != null && proc.isAlive(); }

    private static void info(MinecraftClient mc, String msg) {
        mc.execute(() -> {
            if (mc.player != null)
                mc.player.sendMessage(Text.literal("[Corisande VC] " + msg).formatted(Formatting.GRAY), false);
        });
    }

    public static synchronized void start(MinecraftClient mc, boolean quiet) {
        if (isOn()) { if (!quiet) info(mc, ready ? "Microphone is already on." : "Starting microphone..."); return; }
        if (!System.getProperty("os.name", "").toLowerCase().contains("win")) {
            if (!quiet) info(mc, "Built-in speech recognition currently requires Windows. You can still type to Corisande.");
            return;
        }
        try {
            Path script = Files.createTempFile("corisande-listen", ".ps1");
            Files.writeString(script, SCRIPT, StandardCharsets.UTF_8);
            script.toFile().deleteOnExit();
            ProcessBuilder pb = new ProcessBuilder("powershell.exe", "-NoLogo", "-NoProfile", "-STA",
                    "-ExecutionPolicy", "Bypass", "-File", script.toString());
            pb.redirectErrorStream(true);
            proc = pb.start();
            ready = false;
            if (!hookAdded) {
                hookAdded = true;
                Runtime.getRuntime().addShutdownHook(new Thread(VoiceListener::stop));
            }
            final Process mine = proc;
            Thread reader = new Thread(() -> {
                try (BufferedReader r = new BufferedReader(new InputStreamReader(mine.getInputStream(), StandardCharsets.UTF_8))) {
                    String line;
                    while ((line = r.readLine()) != null) {
                        if (line.startsWith("READY")) {
                            ready = true;
                            info(mc, "Listening. Talk normally to Corisande. Press V to mute.");
                        } else if (line.startsWith("ERROR:")) {
                            info(mc, "Microphone error: " + line.substring(6));
                        } else if (line.startsWith("HEARD:")) {
                            String spoken = line.substring(6).replaceAll("[^A-Za-z0-9 .,!?'-]", " ").replaceAll("\\s+", " ").trim();
                            if (spoken.isEmpty() || Tts.isSpeaking()) continue;
                            mc.execute(() -> {
                                if (mc.player != null && mc.getNetworkHandler() != null)
                                    mc.getNetworkHandler().sendChatCommand("corisande " + spoken);
                            });
                        }
                    }
                } catch (Exception ignored) {
                } finally {
                    ready = false;
                    if (proc == mine) {
                        proc = null;
                        info(mc, "Voice listener stopped.");
                    }
                }
            }, "fromthehorror-voice");
            reader.setDaemon(true);
            reader.start();
            if (!quiet) info(mc, "Turning microphone on...");
        } catch (Exception e) {
            proc = null;
            ready = false;
            info(mc, "Could not start speech recognition: " + e.getMessage());
        }
    }

    public static synchronized void stop() {
        ready = false;
        Process current = proc;
        proc = null;
        if (current != null) {
            current.destroy();
            try {
                if (!current.waitFor(300, java.util.concurrent.TimeUnit.MILLISECONDS)) current.destroyForcibly();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                current.destroyForcibly();
            }
        }
    }
}
''', encoding="utf-8")

client = root / "FromTheHorrorClient.java"
s = client.read_text(encoding="utf-8")
if "ClientPlayConnectionEvents.JOIN.register" not in s:
    anchor = "        ClientPlayConnectionEvents.DISCONNECT.register((handler, client) -> VoiceListener.stop());"
    if anchor not in s:
        raise SystemExit("Could not find client disconnect hook")
    s = s.replace(anchor, """        // Automatically listen whenever the player enters a world. V toggles the microphone.
        ClientPlayConnectionEvents.JOIN.register((handler, sender, client) -> VoiceListener.start(client, true));
""" + anchor, 1)
s = s.replace('key.fromthehorror.voice_settings', 'key.fromthehorror.voice_settings')
client.write_text(s, encoding="utf-8")

lang = Path("src/main/resources/assets/fromthehorror/lang/en_us.json")
data = json.loads(lang.read_text(encoding="utf-8"))
data["key.fromthehorror.voice_settings"] = "Toggle Corisande Microphone (V)"
data["category.fromthehorror"] = "From The Horror"
lang.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print("Voice listener now auto-starts on world join; V mutes/unmutes; PowerShell event output and microphone errors handled.")
