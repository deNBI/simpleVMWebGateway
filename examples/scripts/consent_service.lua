local session = require("resty.session")

local _M = {}

-- Valid return_to URLs: must start with '/', no '//', no '\', no control characters,
-- and not be a system control endpoint.
local function is_valid_return_to(url)
    if not url or type(url) ~= "string" then return false end
    if url == "/" then return true end
    if not url:find("^/") then return false end
    if url:find("//") or url:find("\\") then return false end
    if url:find("[%z-\x1f\x7f]") then return false end

    local forbidden = { "/consent", "/consent/callback", "/redirect_uri" }
    for _, path in ipairs(forbidden) do
        if url == path then return false end
    end
    return true
end

function _M.check_consent()
    local sess = session.new()
    if not sess then
        ngx.log(ngx.ERR, "Failed to initialize session in check_consent")
        return
    end

    local now = os.time()
    local consent_given = sess.data.consent_given
    local consent_at = sess.data.consent_at or 0

    -- Consent is valid if given and not older than 86400 seconds (24 hours)
    if not consent_given or (now - consent_at > 86400) then
        local return_to = ngx.var.request_uri or "/"
        ngx.redirect("/consent?return_to=" .. ngx.escape_uri(return_to), true)
        ngx.exit(ngx.HTTP_MOVED_TEMPORARILY)
    end
end

function _M.render_consent_page()
    local sess = session.new()
    local args = ngx.req.get_uri_args()
    local return_to = args["return_to"]

    if not is_valid_return_to(return_to) then
        return_to = "/"
    end

    sess.data.showing_consent = true
    sess.data.consent_return_to = return_to
    sess:commit()

    ngx.header.content_type = "text/html; charset=utf-8"
    ngx.say([[
<!DOCTYPE html>
<html>
<head>
    <title>Consent Required</title>
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f4f4f9; }
        .card { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 500px; text-align: center; }
        h1 { color: #333; }
        p { color: #666; line-height: 1.5; margin-bottom: 2rem; }
        .btn { background: #007bff; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 4px; cursor: pointer; font-size: 1rem; }
        .btn:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Terms of Service</h1>
        <p>By proceeding, you agree to our terms of service and privacy policy. You acknowledge that your identity will be verified via OIDC.</p>
        <form method="POST" action="/consent/callback">
            <button type="submit" class="btn">I Agree & Continue</button>
        </form>
    </div>
</body>
</html>
    ]])
end

function _M.handle_consent_post()
    local sess = session.new()

    if not sess.data.showing_consent then
        ngx.status = ngx.HTTP_FORBIDDEN
        ngx.say("Forbidden: No consent flow active")
        ngx.exit(ngx.HTTP_FORBIDDEN)
    end

    sess.data.consent_given = true
    sess.data.consent_at = os.time()

    local return_to = sess.data.consent_return_to or "/"

    -- Cleanup temporary flow data
    sess.data.showing_consent = nil
    sess.data.consent_return_to = nil
    sess:commit()

    ngx.redirect(return_to, true) -- 303 See Other
    ngx.exit(ngx.HTTP_SEE_OTHER)
end

return _M
