-- examples/scripts/consent_html.lua
local _M = {}

function _M.render()
    return[[
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consent Required</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            margin: 0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Roboto,
                Helvetica,
                Arial,
                sans-serif;
            background: #ffffff;
            color: #222633;
        }
        .card {
            width: 100%;
            max-width: 800px;
            background: #ffffff;
            border: 1px solid #DCDDE5;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 6px 20px rgba(34, 38, 48, 0.12);
        }
        .card-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            background: #222630;
            padding: 1.25rem 2rem;
        }
        .logo {
            width: 54px;
            height: 54px;
            object-fit: contain;
        }
        .brand {
            color: #D0E9EA;
            font-size: 1.65rem;
            font-weight: 400;
            letter-spacing: -0.02em;
        }
        .brand strong {
            font-weight: 600;
        }
        .card-body {
            padding: 2rem;
        }
        .notice {
            padding: 1.25rem;
            margin-bottom: 1.5rem;
            background: #D0E9EA;
            color: #254B4C;
            border-radius: 4px;
            line-height: 1.55;
        }
        .notice strong {
            color: #222633;
        }
        p {
            color: #343A48;
            line-height: 1.6;
            margin: 0 0 1.25rem;
        }
        a {
            color: #254B4C;
            font-weight: 600;
            text-decoration: underline;
            text-underline-offset: 2px;
        }
        a:hover {
            text-decoration-thickness: 2px;
        }
        form {
            margin-top: 2rem;
        }
        .btn {
            width: 100%;
            padding: 0.85rem 1.5rem;

            border: none;
            border-radius: 4px;

            background: #2A888D;
            color: #ffffff;

            font-size: 1rem;
            font-weight: 600;

            cursor: pointer;
            transition: background 0.15s ease;
        }
        .btn:hover {
            background: #2D313D;
        }
        .btn:focus-visible,
        a:focus-visible {
            outline: 3px solid #D0E9EA;
            outline-offset: 3px;
        }
        @media (max-width: 600px) {
            body {
                padding: 1rem;
            }
            .card-header,
            .card-body {
                padding: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <main class="card">
        <div class="card-header">
            <img
                src="https://simplevm.denbi.de/portal/webapp/assets/simplevm_favicon.png"
                alt="SimpleVM Logo"
                class="logo"
            >
            <span class="brand">
                <strong>SimpleVM</strong> Web Services
            </span>
        </div>
        <div class="card-body">
        <p>
            The service you are about to access is provided by its users.
            Neither SimpleVM nor de.NBI Cloud is responsible for the content
            provided through this service.
            <br/><br/>
            By continuing, you agree to the
                <a
                    href="https://cloud.denbi.de/about/policies/"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Terms of Service and Privacy Policy
                </a>.
            </p>

            <form method="POST" action="/consent/callback">
                <button type="submit" class="btn">
                    Agree and Continue
                </button>
            </form>

        </div>
    </main>
</body>
</html>
    ]]
end

return _M