package cn.resourcepack;

import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerCommandPreprocessEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.scheduler.BukkitRunnable;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URI;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.UUID;

import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.configuration.file.YamlConfiguration;

import static cn.resourcepack.Resourcepack.SHA1ToUUIDConverter.sha1ToUUID;


public class Resourcepack extends JavaPlugin implements Listener {

    private FileConfiguration config;

    @Override
    public void onEnable() {
        getLogger().info("Plugin enabled!");
        getServer().getPluginManager().registerEvents(this, this);

        // Load or create config.yml
        if (!getDataFolder().exists()) {
            getDataFolder().mkdirs();
        }
        File configFile = new File(getDataFolder(), "config.yml");
        if (!configFile.exists()) {
            try {
                configFile.createNewFile();
                FileWriter writer = new FileWriter(configFile);
                writer.write("url: http://127.0.0.1:5000\nid: iJvtF1a5846f");
                writer.close();
            } catch (IOException e) {
                getLogger().warning("Failed to create config.yml: " + e.getMessage());
            }
        }
        config = YamlConfiguration.loadConfiguration(configFile);
    }

    @Override
    public void onDisable() {
        getLogger().info("Plugin disabled!");
    }
    public static class SHA1ToUUIDConverter implements Listener {
        public static UUID sha1ToUUID(String input) throws NoSuchAlgorithmException {
            MessageDigest digest = MessageDigest.getInstance("SHA-1");
            byte[] hash = digest.digest(input.getBytes());
            long mostSignificantBits = 0;
            long leastSignificantBits = 0;
            for (int i = 0; i < 8; i++) {
                mostSignificantBits = (mostSignificantBits << 8) | (hash[i] & 0xff);
            }
            for (int i = 8; i < 16; i++) {
                leastSignificantBits = (leastSignificantBits << 8) | (hash[i] & 0xff);
            }
            return new UUID(mostSignificantBits, leastSignificantBits);
        }
    }
    @EventHandler
    public void onPlayerCommand(PlayerCommandPreprocessEvent event) {
        Player player = event.getPlayer();
        String[] args = event.getMessage().split(" ");
        if (args.length > 0 && args[0].equalsIgnoreCase("/getpack")) {
            event.setCancelled(true); // 取消命令执行
            // 异步执行获取资源包下载链接的任务
            new BukkitRunnable() {
                @Override
                public void run() {
                    String downloadUrl = getDownloadUrl();
                    if (downloadUrl != null) {
                        // 更新玩家资源包
                        String sha1_ = null;
                        URI uri = null;
                        try {
                            URL url = new URL(downloadUrl);
                            sha1_ = url.getRef();
                            uri = new URI(url.getProtocol(), url.getUserInfo(), url.getHost(), url.getPort(), url.getPath(), url.getQuery(), null);
                            String url_ = uri.toString();

                        } catch (Exception e) {
                            e.printStackTrace();
                        }

//                        player.setResourcePack(downloadUrl);
                        UUID uuid = null;
                        try {
                            if (sha1_ != null) {
                                uuid = sha1ToUUID(sha1_);
                            }
                        } catch (NoSuchAlgorithmException e) {
                            throw new RuntimeException(e);
                        }
                        player.sendResourcePacks(new CustomResourcePackInfo(uuid, uri, sha1_));
                    } else {
                        // 发送失败消息给玩家
                        player.sendMessage("获取资源包下载链接失败，请稍后重试");
                    }
                }
            }.runTaskAsynchronously(this);
        }
    }

    @EventHandler
    public void onPlayerJoin(PlayerJoinEvent event) {
        Player player = event.getPlayer();
        // 异步执行获取资源包下载链接的任务
        new BukkitRunnable() {
            @Override
            public void run() {
                String downloadUrl = getDownloadUrl();
                if (downloadUrl != null) {
                    // 更新玩家资源包
                    String sha1_ = null;
                    URI uri = null;
                    try {
                        URL url = new URL(downloadUrl);
                        sha1_ = url.getRef();
                        uri = new URI(url.getProtocol(), url.getUserInfo(), url.getHost(), url.getPort(), url.getPath(), url.getQuery(), null);
                        String url_ = uri.toString();

                    } catch (Exception e) {
                        e.printStackTrace();
                    }

//                        player.setResourcePack(downloadUrl);
                    UUID uuid = null;
                    try {
                        if (sha1_ != null) {
                            uuid = sha1ToUUID(sha1_);
                        }
                    } catch (NoSuchAlgorithmException e) {
                        throw new RuntimeException(e);
                    }
                    player.sendResourcePacks(new CustomResourcePackInfo(uuid, uri, sha1_));
                } else {
                    // 发送失败消息给玩家
                    player.sendMessage("下载资源包失败，请重新加入服务器");
                }
            }
        }.runTaskAsynchronously(this);
    }

    private String getDownloadUrl() {
        String apiUrl = config.getString("url") + "/download_url?id=" + config.getString("id");
        try {
            URL url = new URL(apiUrl);
            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setRequestMethod("GET");
            con.setRequestProperty("User-Agent", "Mozilla/5.0");
            int responseCode = con.getResponseCode();
            if (responseCode == HttpURLConnection.HTTP_OK) {
                BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()));
                String inputLine;
                StringBuilder response = new StringBuilder();
                while ((inputLine = in.readLine()) != null) {
                    response.append(inputLine);
                }
                in.close();
                return response.toString();
            } else {
                getLogger().warning("API请求失败，错误代码：" + responseCode);
                return null;
            }
        } catch (Exception e) {
            getLogger().warning("获取下载链接时出现异常：" + e.getMessage());
            return null;
        }
    }
}

