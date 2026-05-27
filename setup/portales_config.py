PORTALES = {
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
        "login_url": "https://www.remotelatinos.com/login",
        "home_url": "https://www.remotelatinos.com",
        "login_exitoso_url": "/jobs",
        "login_exitoso_selector": "a[href*='logout'], a[href*='profile'], .user-menu",
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
