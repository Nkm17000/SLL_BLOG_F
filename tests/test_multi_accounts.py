import json
from pathlib import Path
from app.config import Config

def test_social_accounts_reads_multiple_configured_destinations(tmp_path, monkeypatch):
    cfg = tmp_path / 'social_accounts.json'
    cfg.write_text(json.dumps({
        'facebook': [
            {'name':'Page A','id_env':'FB_A_ID','token_env':'FB_A_TOKEN','enabled':True},
            {'name':'Page B','id_env':'FB_B_ID','token_env':'FB_B_TOKEN','enabled':True},
            {'name':'Disabled','id_env':'FB_C_ID','token_env':'FB_C_TOKEN','enabled':False}
        ],
        'instagram': [
            {'name':'Insta A','id_env':'IG_A_ID','token_env':'IG_A_TOKEN','enabled':True}
        ]
    }), encoding='utf-8')
    monkeypatch.setattr(Config, 'SOCIAL_ACCOUNTS_PATH', str(cfg))
    for k,v in {'FB_A_ID':'1','FB_A_TOKEN':'a','FB_B_ID':'2','FB_B_TOKEN':'b','FB_C_ID':'3','FB_C_TOKEN':'c','IG_A_ID':'4','IG_A_TOKEN':'d'}.items():
        monkeypatch.setenv(k,v)
    accounts=Config.social_accounts()
    assert [x['id'] for x in accounts['facebook']] == ['1','2']
    assert [x['id'] for x in accounts['instagram']] == ['4']

def test_missing_credentials_are_skipped(tmp_path, monkeypatch):
    cfg=tmp_path/'social_accounts.json'
    cfg.write_text(json.dumps({'facebook':[{'name':'No creds','id_env':'NO_ID','token_env':'NO_TOKEN','enabled':True}],'instagram':[]}), encoding='utf-8')
    monkeypatch.setattr(Config, 'SOCIAL_ACCOUNTS_PATH', str(cfg))
    monkeypatch.delenv('NO_ID', raising=False); monkeypatch.delenv('NO_TOKEN', raising=False)
    monkeypatch.setattr(Config, 'FACEBOOK_PAGE_ID', '')
    monkeypatch.setattr(Config, 'FACEBOOK_PAGE_TOKEN', '')
    assert Config.social_accounts()['facebook'] == []
