local session = require("resty.session")

math.randomseed(os.time())

local _M = {}

-- Helper to generate a random token
local function generate_token(length)
    local chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    local token = ""
    for i = 1, length do
        local rand = math.random(1, #chars)
        token = token .. chars:sub(rand, rand)
    end
    return token
end

-- Helper to validate relative path
local function is_relative_path(path)
    if not path then return false end
    -- Must start with / and not //
    return path:find("^/") and not path:find("^//")
end

function _M.check_consent()
    local sess = session.new()
    if sess.data and sess.data.consent_given then
        return true
    end

    -- Consent missing, redirect to /consent
    local return_to = ngx.var.uri .. (ngx.var.args and "?" .. ngx.var.args or "")
    ngx.redirect("/consent?return_to=" .. ngx.escape_uri(return_to))
    return false
end

function _M.render_consent_page(return_to)
    local sess = session.new()

    -- Generate and store CSRF token
    local csrf_token = generate_token(32)
    sess.data = sess.data or {}
    sess.data.consent_csrf = csrf_token
    sess:save()

    ngx.header.content_type = "text/html; charset=utf-8"

    local html = [[
    <!DOCTYPE html>
    <html>
    <head>
        <title>Consent Required</title>
        <style>
            body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f4f4f9; }
            .container { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 600px; text-align: center; }
            h1 { color: #333; }
            p { color: #666; line-height: 1.6; margin-bottom: 2rem; }
            .btn { background: #007bff; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 4px; cursor: pointer; font-size: 1rem; }
            .btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Disclaimer / Notice</h1>
            <p>
                By proceeding, you acknowledge and agree to the terms of use of this service.
                Please ensure you are authorized to access the requested resources.
            </p>
            <form method="POST" action="/consent/callback">
                <input type="hidden" name="csrf_token" value="]] .. csrf_token .. [[">
                <input type="hidden" name="return_to" value="]] .. (return_to or "/") .. [[">
                <button type="submit" class="btn">I Agree & Proceed</button>
            </form>
        </div>
    </body>
    </html>
    ]]

    ngx.say(html)
end

function _M.handle_consent_post()
    local sess = session.new()
    ngx.req.read_body()
    local args = ngx.req.get_post_args()

    local csrf_token = args["csrf_token"]
    local return_to = args["return_to"]

    -- 1. CSRF Validation
    if not csrf_token or not sess.data or sess.data.consent_csrf ~= csrf_token then
        ngx.status = ngx.HTTP_FORBIDDEN
        ngx.say("Invalid CSRF token")
        return ngx.exit(ngx.HTTP_FORBIDDEN)
    end

    -- 2. Relative Path Validation
    if not is_relative_path(return_to) then
        ngx.status = ngx.HTTP_BAD_REQUEST
        ngx.say("Invalid return path")
        return ngx.exit(ngx.HTTP_BAD_REQUEST)
    end

    -- 3. Set Consent
    sess.data = sess.data or {}
    sess.data.consent_given = true
    -- Note: session expiry is handled by the global session config (86400s)
    sess:save()

    -- 4. Redirect back
    return ngx.redirect(return_to)
end

return _M
