class DocumentRequestExternal:
    def __init__(self, document_url: str, webhook_url: str):
        self.document_url = document_url
        self.webhook_url = webhook_url if webhook_url else "https://strong-states-invite.loca.lt"
