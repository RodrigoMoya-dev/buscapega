PORTALES = {
    "findjobit": {
        "nombre": "FindJobIT",
        # FindJobIT redirige /job-seekers/login → /job-seekers incluso SIN autenticar,
        # lo que engaña a Strategy 1. Usamos la página de perfil (requiere auth real)
        # y "skip_strategy_1": True para forzar que el usuario siempre haga login manual.
        "login_url": "https://www.findjobit.com/job-seekers/login",
        "home_url": "https://www.findjobit.com",
        "login_exitoso_url": "/job-seekers/profile",  # solo accesible tras auth real
        "login_exitoso_selector": "[href*='/job-seekers/logout'], [href*='signout'], "
                                  ".avatar, [class*='avatar'], [class*='user-menu'], "
                                  "[data-cy*='user'], img[alt*='profile' i]",
        "skip_strategy_1": True,  # no inferir login desde redirect, siempre confirmar
    },
    "getonbrd": {
        "nombre": "GetOnBrd",
        "login_url": "https://www.getonbrd.com/sessions/new",
        "home_url": "https://www.getonbrd.com",
        "login_exitoso_url": "/search",          # URL a la que redirige tras login exitoso
        "login_exitoso_selector": "a[href*='/account'], [data-cy='user-menu'], .user-avatar",
    },
    "tecnoempleo": {
        "nombre": "Tecnoempleo",
        "login_url": "https://www.tecnoempleo.com/login.php",
        "home_url": "https://www.tecnoempleo.com",
        "login_exitoso_url": "/ofertas-trabajo",
        "login_exitoso_selector": "a[href*='logout'], #user-menu, .mi-cuenta",
    },
    "remotelatinos": {
        "nombre": "RemoteLatinos",
        "login_url": "https://app.remotelatinos.com/auth/login",
        "home_url": "https://app.remotelatinos.com",
        "login_exitoso_url": "/dashboard",
        "login_exitoso_selector": (
            "a[href*='logout'], button:has-text('Log out'), "
            "a[href*='/profile'], img[alt*='avatar' i], "
            "[data-testid*='user'], .user-menu, .avatar"
        ),
        # Google OAuth puede redirigir de /auth/login incluso sin autenticar
        "skip_strategy_1": True,
    },
    "chiletrabajos": {
        "nombre": "ChileTrabajos",
        "login_url": "https://www.chiletrabajos.cl/login",
        "home_url": "https://www.chiletrabajos.cl",
        "login_exitoso_url": "/ofertas",
        "login_exitoso_selector": "a[href*='logout'], .user-info, #user-panel",
    },
    "chumiit": {
        "nombre": "Chumi-IT",
        "login_url": "https://chumi-it.com/login",
        "home_url": "https://chumi-it.com",
        "login_exitoso_url": "/jobs",
        "login_exitoso_selector": "a[href*='logout'], .user-menu, .profile-link",
    },
}
