class UserEventType:
    MESSAGE_UNREAD = "message:unread"
    CHANNEL_CREATE = "channel:create"  # private, dm, group_dm
    MENTION_CREATE = "mention:create"
    CHANNEL_ROLE_UPDATE = "channel:role:update"
    WORKSPACE_REMOVE = "workspace:remove"


class WorkspaceEventType:
    WORKSPACE_UPDATE = "workspace:update"
    WORKSPACE_DELETE = "workspace:delete"
    WORKSPACE_TRANSFER = "workspace:transfer"
    WORKSPACE_JOIN = "workspace:join"
    WORKSPACE_LEAVE = "workspace:leave"
    WORKSPACE_ROLE_UPDATE = "workspace:role:update"
    CHANNEL_CREATE = "channel:create"  # public


class ChannelEventType:
    CHANNEL_UPDATE = "channel:update"
    CHANNEL_DELETE = "channel:delete"
    CHANNEL_TRANSFER = "channel:transfer"
    CHANNEL_JOIN = "channel:join"
    CHANNEL_LEAVE = "channel:leave"
    MESSAGE_CREATE = "message:create"
    MESSAGE_UPDATE = "message:update"
    MESSAGE_DELETE = "message:delete"
    REACTION_CREATE = "reaction:create"
    REACTION_DELETE = "reaction:delete"
