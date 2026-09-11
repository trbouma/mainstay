"""Localization primitives for the Mainstay Local dashboard."""

from __future__ import annotations

import re
from collections.abc import Callable

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = {
    "en": "English",
    "fr": "Français",
    "es": "Español",
    "pt": "Português",
    "de": "Deutsch",
    "it": "Italiano",
    "zh-Hans": "简体中文",
}

_LANGUAGE_TAG_PATTERN = re.compile(
    r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$"
)

_ENGLISH = {
    "tagline": "There's no place like home.",
    "language": "Language",
    "api_endpoints": "API endpoints",
    "identity": "Identity",
    "health": "Health",
    "registry": "Registry",
    "status_json": "Status JSON",
    "mainstay_installation": "Mainstay installation",
    "installation_role": "Installation identity and local control plane",
    "installation_identity_unavailable": "Installation identity unavailable",
    "unavailable": "Unavailable",
    "service_network": "Service network",
    "services_summary": "Services coordinated inside this installation: {count}",
    "checking_services": "Checking services",
    "registry_detail": "Registry: {name}",
    "control_plane": "Control plane: port {port}",
    "waiting_first_check": "Waiting for first check",
    "required_bootstrap": "Required bootstrap step",
    "confirm_reserve": "Confirm Lightning fee reserve",
    "reserve_explanation": (
        "The service Acorn needs at least {amount} sats of operator-funded "
        "reserve to cover mint input fees while delivering Lightning-address "
        "payments. A healthy worker can create invoices before this reserve "
        "exists."
    ),
    "reserve_instruction": (
        "Mainstay does not yet measure the reserve automatically. Check it "
        "from the deployment host with ./reserve-balance.sh, fund it after "
        "first startup, and replenish it as fees consume it."
    ),
    "disabled": "Disabled",
    "checking": "Checking",
    "operator": "Operator",
    "internal": "Internal",
    "local": "Local",
    "external": "External",
    "available": "Available",
    "all_services_available": "All services available",
    "service_attention_needed": "Service attention needed",
    "status_check_failed": "Status check failed",
    "checked_at": "Checked {time}",
    "service_report_unavailable": "Service report unavailable",
    "homepage_unreadable": "The homepage could not be read.",
    "service_report": "Service report",
}

_FRENCH = {
    "tagline": "On n'est jamais mieux que chez soi.",
    "language": "Langue",
    "api_endpoints": "Points de terminaison de l’API",
    "identity": "Identité",
    "health": "État",
    "registry": "Registre",
    "status_json": "État JSON",
    "mainstay_installation": "Installation Mainstay",
    "installation_role": "Identité de l’installation et plan de contrôle local",
    "installation_identity_unavailable": "Identité de l’installation indisponible",
    "unavailable": "Indisponible",
    "service_network": "Réseau de services",
    "services_summary": "Services coordonnés dans cette installation : {count}",
    "checking_services": "Vérification des services",
    "registry_detail": "Registre : {name}",
    "control_plane": "Plan de contrôle : port {port}",
    "waiting_first_check": "En attente de la première vérification",
    "required_bootstrap": "Étape d’amorçage requise",
    "confirm_reserve": "Confirmer la réserve pour les frais Lightning",
    "reserve_explanation": (
        "L’Acorn de service a besoin d’une réserve d’au moins {amount} sats "
        "financée par l’opérateur pour couvrir les frais d’entrée du service "
        "de monnaie lors de la livraison de paiements à une adresse Lightning. "
        "Un processus sain peut créer des factures avant que cette réserve "
        "n’existe."
    ),
    "reserve_instruction": (
        "Mainstay ne mesure pas encore cette réserve automatiquement. "
        "Vérifiez-la depuis l’hôte de déploiement avec ./reserve-balance.sh, "
        "approvisionnez-la après le premier démarrage et renflouez-la à mesure "
        "que les frais la consomment."
    ),
    "disabled": "Désactivé",
    "checking": "Vérification",
    "operator": "Exploitant",
    "internal": "Interne",
    "local": "Local",
    "external": "Externe",
    "available": "Disponible",
    "all_services_available": "Tous les services sont disponibles",
    "service_attention_needed": "Certains services nécessitent une attention",
    "status_check_failed": "Échec de la vérification de l’état",
    "checked_at": "Vérifié à {time}",
    "service_report_unavailable": "Rapport du service indisponible",
    "homepage_unreadable": "La page d’accueil n’a pas pu être lue.",
    "service_report": "Rapport du service",
}

_SPANISH = {
    "tagline": "No hay lugar como el hogar.",
    "language": "Idioma",
    "api_endpoints": "Puntos de acceso de la API",
    "identity": "Identidad",
    "health": "Estado",
    "registry": "Registro",
    "status_json": "Estado JSON",
    "mainstay_installation": "Instalación Mainstay",
    "installation_role": "Identidad de la instalación y plano de control local",
    "installation_identity_unavailable": "Identidad de la instalación no disponible",
    "unavailable": "No disponible",
    "service_network": "Red de servicios",
    "services_summary": "Servicios coordinados en esta instalación: {count}",
    "checking_services": "Comprobando servicios",
    "registry_detail": "Registro: {name}",
    "control_plane": "Plano de control: puerto {port}",
    "waiting_first_check": "Esperando la primera comprobación",
    "required_bootstrap": "Paso de inicialización obligatorio",
    "confirm_reserve": "Confirmar la reserva para comisiones Lightning",
    "reserve_explanation": (
        "El Acorn de servicio necesita una reserva de al menos {amount} sats "
        "financiada por el operador para cubrir las comisiones de entrada del "
        "servicio de moneda al entregar pagos a direcciones Lightning. Un "
        "proceso en buen estado puede crear facturas antes de que exista esta "
        "reserva."
    ),
    "reserve_instruction": (
        "Mainstay aún no mide la reserva automáticamente. Compruébela desde "
        "el host de despliegue con ./reserve-balance.sh, finánciela después "
        "del primer inicio y repóngala a medida que las comisiones la consuman."
    ),
    "disabled": "Desactivado",
    "checking": "Comprobando",
    "operator": "Operador",
    "internal": "Interno",
    "local": "Local",
    "external": "Externo",
    "available": "Disponible",
    "all_services_available": "Todos los servicios están disponibles",
    "service_attention_needed": "Algunos servicios requieren atención",
    "status_check_failed": "Falló la comprobación del estado",
    "checked_at": "Comprobado a las {time}",
    "service_report_unavailable": "Informe del servicio no disponible",
    "homepage_unreadable": "No se pudo leer la página de inicio.",
    "service_report": "Informe del servicio",
}

_PORTUGUESE = {
    "tagline": "Não há lugar como o nosso lar.",
    "language": "Idioma",
    "api_endpoints": "Endpoints da API",
    "identity": "Identidade",
    "health": "Estado",
    "registry": "Registro",
    "status_json": "Estado JSON",
    "mainstay_installation": "Instalação Mainstay",
    "installation_role": "Identidade da instalação e plano de controle local",
    "installation_identity_unavailable": "Identidade da instalação indisponível",
    "unavailable": "Indisponível",
    "service_network": "Rede de serviços",
    "services_summary": "Serviços coordenados nesta instalação: {count}",
    "checking_services": "Verificando serviços",
    "registry_detail": "Registro: {name}",
    "control_plane": "Plano de controle: porta {port}",
    "waiting_first_check": "Aguardando a primeira verificação",
    "required_bootstrap": "Etapa de inicialização obrigatória",
    "confirm_reserve": "Confirmar a reserva para taxas Lightning",
    "reserve_explanation": (
        "O Acorn de serviço precisa de uma reserva de pelo menos {amount} sats "
        "financiada pelo operador para cobrir as taxas de entrada do serviço "
        "de moeda ao entregar pagamentos para endereços Lightning. Um processo "
        "saudável pode criar faturas antes que essa reserva exista."
    ),
    "reserve_instruction": (
        "O Mainstay ainda não mede a reserva automaticamente. Verifique-a no "
        "host de implantação com ./reserve-balance.sh, financie-a após a "
        "primeira inicialização e reponha-a à medida que as taxas a consumirem."
    ),
    "disabled": "Desativado",
    "checking": "Verificando",
    "operator": "Operador",
    "internal": "Interno",
    "local": "Local",
    "external": "Externo",
    "available": "Disponível",
    "all_services_available": "Todos os serviços estão disponíveis",
    "service_attention_needed": "Alguns serviços precisam de atenção",
    "status_check_failed": "Falha na verificação do estado",
    "checked_at": "Verificado às {time}",
    "service_report_unavailable": "Relatório do serviço indisponível",
    "homepage_unreadable": "Não foi possível ler a página inicial.",
    "service_report": "Relatório do serviço",
}

_GERMAN = {
    "tagline": "Zu Hause ist es doch am schönsten.",
    "language": "Sprache",
    "api_endpoints": "API-Endpunkte",
    "identity": "Identität",
    "health": "Zustand",
    "registry": "Verzeichnis",
    "status_json": "Status-JSON",
    "mainstay_installation": "Mainstay-Installation",
    "installation_role": "Installationsidentität und lokale Steuerungsebene",
    "installation_identity_unavailable": "Installationsidentität nicht verfügbar",
    "unavailable": "Nicht verfügbar",
    "service_network": "Dienstnetzwerk",
    "services_summary": "In dieser Installation koordinierte Dienste: {count}",
    "checking_services": "Dienste werden geprüft",
    "registry_detail": "Verzeichnis: {name}",
    "control_plane": "Steuerungsebene: Port {port}",
    "waiting_first_check": "Warten auf die erste Prüfung",
    "required_bootstrap": "Erforderlicher Initialisierungsschritt",
    "confirm_reserve": "Lightning-Gebührenreserve bestätigen",
    "reserve_explanation": (
        "Der Dienst-Acorn benötigt eine vom Betreiber finanzierte Reserve von "
        "mindestens {amount} sats, um die Eingangsgebühren des Gelddienstes bei "
        "der Zustellung von Zahlungen an Lightning-Adressen zu decken. Ein "
        "fehlerfrei laufender Prozess kann Rechnungen erstellen, bevor diese "
        "Reserve vorhanden ist."
    ),
    "reserve_instruction": (
        "Mainstay misst die Reserve noch nicht automatisch. Prüfen Sie sie auf "
        "dem Bereitstellungshost mit ./reserve-balance.sh, finanzieren Sie sie "
        "nach dem ersten Start und füllen Sie sie auf, wenn Gebühren sie "
        "verbrauchen."
    ),
    "disabled": "Deaktiviert",
    "checking": "Wird geprüft",
    "operator": "Betreiber",
    "internal": "Intern",
    "local": "Lokal",
    "external": "Extern",
    "available": "Verfügbar",
    "all_services_available": "Alle Dienste sind verfügbar",
    "service_attention_needed": "Einige Dienste benötigen Aufmerksamkeit",
    "status_check_failed": "Statusprüfung fehlgeschlagen",
    "checked_at": "Geprüft um {time}",
    "service_report_unavailable": "Dienstbericht nicht verfügbar",
    "homepage_unreadable": "Die Startseite konnte nicht gelesen werden.",
    "service_report": "Dienstbericht",
}

_ITALIAN = {
    "tagline": "Nessun posto è come casa.",
    "language": "Lingua",
    "api_endpoints": "Endpoint API",
    "identity": "Identità",
    "health": "Stato",
    "registry": "Registro",
    "status_json": "Stato JSON",
    "mainstay_installation": "Installazione Mainstay",
    "installation_role": "Identità dell’installazione e piano di controllo locale",
    "installation_identity_unavailable": "Identità dell’installazione non disponibile",
    "unavailable": "Non disponibile",
    "service_network": "Rete di servizi",
    "services_summary": "Servizi coordinati in questa installazione: {count}",
    "checking_services": "Verifica dei servizi",
    "registry_detail": "Registro: {name}",
    "control_plane": "Piano di controllo: porta {port}",
    "waiting_first_check": "In attesa della prima verifica",
    "required_bootstrap": "Passaggio di inizializzazione obbligatorio",
    "confirm_reserve": "Conferma la riserva per le commissioni Lightning",
    "reserve_explanation": (
        "L’Acorn di servizio richiede una riserva di almeno {amount} sats "
        "finanziata dall’operatore per coprire le commissioni in entrata del "
        "servizio monetario durante la consegna di pagamenti a indirizzi "
        "Lightning. Un processo integro può creare fatture prima che questa "
        "riserva sia disponibile."
    ),
    "reserve_instruction": (
        "Mainstay non misura ancora automaticamente la riserva. Verificala "
        "dall’host di distribuzione con ./reserve-balance.sh, finanziala dopo "
        "il primo avvio e reintegrala man mano che le commissioni la consumano."
    ),
    "disabled": "Disattivato",
    "checking": "Verifica in corso",
    "operator": "Operatore",
    "internal": "Interno",
    "local": "Locale",
    "external": "Esterno",
    "available": "Disponibile",
    "all_services_available": "Tutti i servizi sono disponibili",
    "service_attention_needed": "Alcuni servizi richiedono attenzione",
    "status_check_failed": "Verifica dello stato non riuscita",
    "checked_at": "Verificato alle {time}",
    "service_report_unavailable": "Rapporto del servizio non disponibile",
    "homepage_unreadable": "Impossibile leggere la pagina iniziale.",
    "service_report": "Rapporto del servizio",
}

_SIMPLIFIED_CHINESE = {
    "tagline": "没有什么地方比得上家。",
    "language": "语言",
    "api_endpoints": "API 端点",
    "identity": "标识",
    "health": "健康状态",
    "registry": "注册表",
    "status_json": "状态 JSON",
    "mainstay_installation": "Mainstay 实例",
    "installation_role": "实例标识与本地控制平面",
    "installation_identity_unavailable": "实例标识不可用",
    "unavailable": "不可用",
    "service_network": "服务网络",
    "services_summary": "此实例协调的服务数量：{count}",
    "checking_services": "正在检查服务",
    "registry_detail": "注册表：{name}",
    "control_plane": "控制平面：端口 {port}",
    "waiting_first_check": "等待首次检查",
    "required_bootstrap": "必需的初始化步骤",
    "confirm_reserve": "确认 Lightning 手续费储备",
    "reserve_explanation": (
        "服务 Acorn 至少需要由运营方提供 {amount} sats 储备，以便在交付至 "
        "Lightning 地址的付款时支付货币服务的输入手续费。即使尚无此储备，"
        "运行正常的进程仍可创建发票。"
    ),
    "reserve_instruction": (
        "Mainstay 尚不能自动测量储备。请在部署主机上使用 "
        "./reserve-balance.sh 检查储备，在首次启动后注资，并随着手续费消耗"
        "及时补充。"
    ),
    "disabled": "已禁用",
    "checking": "正在检查",
    "operator": "运营方",
    "internal": "内部",
    "local": "本地",
    "external": "外部",
    "available": "可用",
    "all_services_available": "所有服务均可用",
    "service_attention_needed": "部分服务需要关注",
    "status_check_failed": "状态检查失败",
    "checked_at": "检查时间：{time}",
    "service_report_unavailable": "服务报告不可用",
    "homepage_unreadable": "无法读取主页。",
    "service_report": "服务报告",
}

_CATALOGS = {
    "en": _ENGLISH,
    "fr": _FRENCH,
    "es": _SPANISH,
    "pt": _PORTUGUESE,
    "de": _GERMAN,
    "it": _ITALIAN,
    "zh-Hans": _SIMPLIFIED_CHINESE,
}

for _language, _catalog in _CATALOGS.items():
    if _catalog.keys() != _ENGLISH.keys():
        missing = sorted(_ENGLISH.keys() - _catalog.keys())
        extra = sorted(_catalog.keys() - _ENGLISH.keys())
        raise RuntimeError(
            f"incomplete {_language} dashboard catalog; "
            f"missing={missing}, extra={extra}"
        )


def normalize_language_tag(value: str) -> str:
    """Return a conservative canonical BCP 47 language tag."""

    candidate = str(value or "").strip()
    if not _LANGUAGE_TAG_PATTERN.fullmatch(candidate):
        raise ValueError("language tag is invalid")
    parts = candidate.split("-")
    normalized = [parts[0].lower()]
    for part in parts[1:]:
        if len(part) == 4 and part.isalpha():
            normalized.append(part.title())
        elif len(part) == 2 and part.isalpha():
            normalized.append(part.upper())
        else:
            normalized.append(part.lower())
    return "-".join(normalized)


def supported_language(value: str | None) -> str:
    """Resolve a supported language, falling back to English."""

    try:
        normalized = normalize_language_tag(value or DEFAULT_LANGUAGE)
    except ValueError:
        return DEFAULT_LANGUAGE
    if normalized in SUPPORTED_LANGUAGES:
        return normalized
    if normalized in {"zh", "zh-CN", "zh-SG"} or normalized.startswith(
        "zh-Hans-"
    ):
        return "zh-Hans"
    base_language = normalized.split("-", 1)[0]
    return base_language if base_language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def resolve_language(explicit: str | None, accept_language: str | None) -> str:
    """Resolve an explicit selector or the strongest supported browser locale."""

    if explicit is not None:
        return supported_language(explicit)

    weighted: list[tuple[float, int, str]] = []
    for index, item in enumerate(str(accept_language or "").split(",")):
        language_range, separator, parameters = item.strip().partition(";")
        if not language_range or language_range == "*":
            continue
        quality = 1.0
        if separator:
            for parameter in parameters.split(";"):
                name, equals, value = parameter.strip().partition("=")
                if name.lower() == "q" and equals:
                    try:
                        quality = float(value)
                    except ValueError:
                        quality = 0.0
        if quality > 0:
            weighted.append((quality, -index, language_range))

    for _quality, _position, language_range in sorted(weighted, reverse=True):
        language = supported_language(language_range)
        if language != DEFAULT_LANGUAGE or language_range.lower().startswith("en"):
            return language
    return DEFAULT_LANGUAGE


def translator(language: str) -> Callable[..., str]:
    """Return a message-key lookup bound to one supported language."""

    catalog = _CATALOGS[supported_language(language)]

    def translate(message_key: str, **values: object) -> str:
        template = catalog.get(message_key, _ENGLISH.get(message_key, message_key))
        return template.format(**values)

    return translate
