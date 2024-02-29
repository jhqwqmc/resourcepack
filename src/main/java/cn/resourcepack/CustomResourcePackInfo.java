package cn.resourcepack;

import net.kyori.adventure.resource.ResourcePackInfo;
import net.kyori.adventure.resource.ResourcePackInfoLike;
import org.jetbrains.annotations.NotNull;

import java.net.URI;
import java.util.UUID;

public class CustomResourcePackInfo implements ResourcePackInfoLike {
    private final UUID id;
    private final URI uri;
    private final String hash;

    public CustomResourcePackInfo(UUID id, URI uri, String hash) {
        this.id = id;
        this.uri = uri;
        this.hash = hash;
    }

    @Override
    public @NotNull ResourcePackInfo asResourcePackInfo() {
        return ResourcePackInfo.resourcePackInfo()
                .id(id)
                .uri(uri)
                .hash(hash)
                .build();
    }

}
