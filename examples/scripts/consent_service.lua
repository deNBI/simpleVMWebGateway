local session = require("resty.session")

local _M = {}

local CONSENT_TTL = 86400

-- Valid return_to URLs: must start with '/', no '//', no '\', no control characters,
-- and not be a system control endpoint.
local function is_valid_return_to(url)
    if not url or type(url) ~= "string" then return false end
    if url == "/" then return true end
    if not url:find("^/") then return false end
    if url:sub(1, 2) == "//" then return false end
    if url:find("\\", 1, true) then return false end
    if url:find("[%z-\x1f\x7f]") then return false end

    local path_without_query = url:match("^([^?]*)")
    local forbidden = { "/consent", "/consent/callback", "/redirect_uri" }
    for _, path in ipairs(forbidden) do
        if path_without_query == path then return false end
    end
    return true
end


function _M.check_consent()
    local sess, err, exists = session.open()

    ngx.log(
    ngx.ERR,
    "CONSENT CHECK: sess=",
    tostring(sess),
    " exists=",
    tostring(exists),
    " err=",
    tostring(err)
    )
    ngx.log(
        ngx.ERR,
        "CONSENT VALUES: given=",
        tostring(consent_given),
        " at=",
        tostring(consent_at)
    )

    if not sess then
        ngx.log(ngx.ERR, "Failed to initialize session: ", err or "unknown")
        return ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
    end

    local consent_given = sess:get("consent_given")
    local consent_at = sess:get("consent_at")

    local consent_valid =
        exists
        and consent_given == true
        and type(consent_at) == "number"
        and ngx.time() - consent_at <= CONSENT_TTL

    if consent_valid then
        return true
    end

    local return_to = ngx.var.request_uri or "/"
    local query = ngx.encode_args({ return_to = return_to })
    return ngx.redirect("/consent?" .. query, ngx.HTTP_FOUND) -- 302 Found
end


function _M.render_consent_page()
    if ngx.req.get_method() ~= "GET" then
        return ngx.exit(ngx.HTTP_NOT_ALLOWED)
    end

    -- Read and validate return_to BEFORE storing it.
    local args = ngx.req.get_uri_args()
    local return_to = args["return_to"]

    if not is_valid_return_to(return_to) then
        return ngx.exit(ngx.HTTP_BAD_REQUEST)
    end

    local sess, err = session.start()

    if not sess then
        ngx.log(ngx.ERR, "Failed to start session: ", err or "unknown")
        return ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
    end

    sess:set("showing_consent", true)
    sess:set("consent_return_to", return_to)

    local ok, save_err = sess:save()
    if not ok then
        ngx.log(ngx.ERR, "Failed to save session: ", save_err or "unknown")
        return ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
    end

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
    local sess, err, exists = session.start()

    if not sess then
        ngx.log(ngx.ERR, "Starting session failed: ", err or "unknown")
        return ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
    end

    if not exists or sess:get("showing_consent") ~= true then
        ngx.status = ngx.HTTP_FORBIDDEN
        ngx.say("Forbidden: No consent flow active")
        return ngx.exit(ngx.HTTP_FORBIDDEN)
    end

    local return_to = sess:get("consent_return_to")
        if not is_valid_return_to(return_to) then
            return ngx.exit(ngx.HTTP_BAD_REQUEST)
        end

    sess:set("consent_given", true)
    sess:set("consent_at", ngx.time())
    sess:set("showing_consent", nil)
    sess:set("consent_return_to", nil)

    local ok, save_err = sess:save()

        if not ok then
            ngx.log(ngx.ERR, "Failed to save consent: ", save_err or "unknown")
            return ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
        end

    return ngx.redirect(return_to, ngx.HTTP_SEE_OTHER) -- 303 See Other
end

return _M
