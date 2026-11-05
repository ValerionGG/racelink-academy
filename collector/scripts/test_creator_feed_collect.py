"""Offline regressions for exact identity/format pairing and conservative access."""
from html import escape
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

from creator_feed_collect import Cards, MAX_CARDS, main, page_cards, permalink, plan_jobs, wildcard_exclusion

def card(url,caption,kind='video',extra=''):
    return ('<div class="sbi_item sbi_type_'+kind+'"><div><a class="sbi_photo" href="'+
            escape(url,quote=True)+'"><img alt="'+escape(caption,quote=True)+'"></a>'+extra+'</div></div>')

class CollectorTests(unittest.TestCase):
    def test_cards_keep_identity_caption_and_type_together(self):
        p=Cards()
        p.feed(card('https://www.instagram.com/p/DY1234567ab/','Premier test #auto')+
               card('https://www.instagram.com/reel/DY1234567ac/?igsh=x','Image du projet','carousel'))
        self.assertEqual([(v['id'],v['publisher_caption'],v['media_type']) for v in p.records],
                         [('instagram:DY1234567ab','Premier test #auto','video'),
                          ('instagram:DY1234567ac','Image du projet','carousel')])

    def test_anchor_spoof_and_conflicting_identity(self):
        for url in ('http://instagram.com/p/DY1234567ab','https://www.instagram.com.evil.test/p/DY1234567ab',
                    'https://user@instagram.com/p/DY1234567ab','https://instagram.com/@test'):
            self.assertIsNone(permalink(url))
        p=Cards()
        p.feed(card('https://instagram.com/reel/DY1234567ab','caption',extra='<a href="https://instagram.com/p/DY9876543ba">other</a>'))
        self.assertEqual(p.records,[])

    def test_placeholder_and_maximum(self):
        p=Cards()
        p.feed(card('https://instagram.com/p/DY1234567ab','Publication 17900625369114579 Instagram')*40)
        self.assertEqual(len(p.records),MAX_CARDS)
        self.assertEqual(p.records[0]['publisher_caption'],'')

    def test_plan_rejects_social_and_repeated_hosts(self):
        j={'creator':'Source','url':'https://www.example.com/'}
        for jobs in ([{**j,'url':'https://www.instagram.com/user/'}],[j,j],[]):
            with self.assertRaises(ValueError): plan_jobs({'jobs':jobs})

    def test_robots_denial_never_fetches_publisher(self):
        with patch('creator_feed_collect.socket.getaddrinfo',return_value=[(0,0,0,'',('8.8.8.8',443))]), \
             patch('creator_feed_collect.read_http',return_value=(200,'text/plain',b'User-agent: *\nDisallow: /')) as fetch:
            with self.assertRaisesRegex(ValueError,'robots_disallow'):
                page_cards({'url':'https://www.example.com/private'})
            self.assertEqual(fetch.call_count,1)

    def test_wildcard_disallows_at_path_end(self):
        lines=['User-agent: *','Disallow: /*.html$ # only HTML']
        self.assertTrue(wildcard_exclusion(lines,'/one/show.html'))
        self.assertFalse(wildcard_exclusion(lines,'/one/show.html/info'))

    def test_checkpoint_blocks_replay_and_different_plan(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name)
            conf=root/'plan.json'
            conf.write_text(json.dumps({'jobs':[{'creator':'Example','url':'https://www.example.com/'}]}))
            argv=['collect',str(conf),'--job','0','--execute','--checkpoint',str(root/'out')]
            with patch.object(sys,'argv',argv),patch('creator_feed_collect.page_cards',return_value={'cards':[]}) as collect:
                main()
                with self.assertRaises(SystemExit):main()
                conf.write_text(conf.read_text()+' ')
                with self.assertRaises(SystemExit):main()
                self.assertEqual(collect.call_count,1)

if __name__=='__main__':unittest.main()
