import shutil
import os
import sys
import eyed3
import tkinter
from xml.etree.cElementTree import parse
from tkinter import filedialog

test_mode = 0

if test_mode:
    local_dir = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
else:
    local_dir = os.path.dirname(os.path.abspath(sys.executable)).replace('\\', '/')

gen_name = ['', 'SOUND VOLTEX BOOTH', 'SOUND VOLTEX II INFINITE INFECTION', 'SOUND VOLTEX III GRAVITY WARS',
            'SOUND VOLTEX IV HEAVENLY HAVEN', 'SOUND VOLTEX V VIVID WAVE', 'SOUND VOLTEX VI EXCEED GEAR']


def get_user_path(title: str) -> str:
    user_root = tkinter.Tk()
    user_root.withdraw()
    user_path = filedialog.askdirectory(title=title)

    if not user_path:
        input('Empty file path')
        sys.exit(-1)

    return user_path.replace('\\', '/')


class Convertor:
    def __init__(self, data_dir, des_dir):
        self.ff_dir = '\"%s/ffmpeg\"' % local_dir
        if not os.path.exists(local_dir + '/ffmpeg.exe'):
            input('ffmpeg not found')
            sys.exit(-1)

        self.xml_dir = data_dir + '/others/music_db.xml'
        self.music_dir = data_dir + '/music/'
        self.folder_list = os.listdir(self.music_dir)
        for poss in self.folder_list:
            if os.path.isfile(self.music_dir + poss):
                self.folder_list.remove(poss)
        self.folder_list = ['0000_dummy'] + self.folder_list
        self.folder_index = 0
        self.dummy_jk = data_dir + '/graphics/jk_dummy_b.png'
        self.des_dir = des_dir + '/'
        self.wma_list = []

        for gen in gen_name:
            if not os.path.exists(self.des_dir + gen):
                os.mkdir(self.des_dir + gen)
            shutil.copyfile(local_dir + '/ffmpeg.exe', self.des_dir + gen + '/ffmpeg.exe')

        self.music_map = []
        jis_xml = open(self.xml_dir, 'r', encoding='cp932').readlines()
        utf_xml = open(self.des_dir + r'/music_db_utf8.xml', 'w', encoding='utf-8')
        utf_xml.write('<?xml version="1.0" encoding="utf-8"?>\n')
        jis_xml.pop(0)
        for line in jis_xml:
            utf_xml.write(line)
        utf_xml.close()

        tree = parse(self.des_dir + r'/music_db_utf8.xml')
        root = tree.getroot()
        index = 0
        while True:
            try:
                mid = int(root[index].attrib['id'])
                # Fuck Shift-JIS
                name = root[index][0][1].text \
                    .replace("驫", "ā").replace("骭", "ü").replace("驩", "Ø").replace("罇", "ê").replace("曩", "è") \
                    .replace("齷", "é").replace("騫", "á").replace("曦", "à").replace("龕", "€").replace("趁", "Ǣ") \
                    .replace("蹇", "₂").replace("彜", "ū").replace("雋", "Ǜ").replace("隍", "Ü").replace("鬻", "♃") \
                    .replace("鬥", "Ã").replace("鬆", "Ý").replace("齶", "♡").replace("齲", "❤").replace("躔", "★") \
                    .replace('釁', '🍄').replace('頽', 'ä')
                artist = root[index][0][3].text \
                    .replace("驫", "ā").replace("骭", "ü").replace("驩", "Ø").replace("罇", "ê").replace("曩", "è") \
                    .replace("齷", "é").replace("騫", "á").replace("曦", "à").replace("龕", "€").replace("趁", "Ǣ") \
                    .replace("蹇", "₂").replace("彜", "ū").replace("雋", "Ǜ").replace("隍", "Ü").replace("鬻", "♃") \
                    .replace("鬥", "Ã").replace("鬆", "Ý").replace("齶", "♡").replace("齲", "❤").replace("躔", "★") \
                    .replace('釁', '🍄').replace('頽', 'ä')
                bpm_max = int(root[index][0][6].text) / 100
                date = root[index][0][8].text
                version = int(root[index][0][13].text)
                inf_lv = int(root[index][1][3][0].text)
                if inf_lv:
                    jk_tag = 4  # Music with a INF diff
                else:
                    jk_tag = 3
                try:
                    mxm_lv = int(root[index][1][4][0].text)
                    if mxm_lv:
                        jk_tag = 5  # Music with a MXM diff
                except IndexError:
                    pass

                self.music_map.append([mid, name, artist, bpm_max, date, version, jk_tag])
                index += 1
            except IndexError:
                break

        os.remove(self.des_dir + r'/music_db_utf8.xml')

    def process(self, map_data: list, ad_hoc: list = None):
        """
        :param map_data: [mid, name, artist, bpm_max, date, version, jk_tag]
        :param ad_hoc:   special arg for musics which have more than 1 sound source
                         [s3v_suf, name]
        """
        mid, name, artist, bpm_max, date, version, jk_tag = map_data

        # Exceptions for multi-source audio
        # GekkouRanbu Kyokuken, Automation paradise(*2), TWO-TORIAL, Help me Erin(holo ver.)
        exception = (709, 927, 1148, 1259, 1438, 1758)
        if not ad_hoc and (mid in exception):
            return

        # Get jacket and raw audio
        mid_4 = str(mid).zfill(4)
        jk_path = self.dummy_jk
        music_folder = ''
        if ad_hoc:
            self.folder_index = 1
        while True:
            folder_id = int(self.folder_list[self.folder_index][:4])
            if folder_id == mid:
                music_folder = self.folder_list[self.folder_index]
            if mid < folder_id:
                break
            self.folder_index += 1

        if not music_folder:
            return
        music_path = self.music_dir + music_folder + '/'
        s3v_path = music_path + music_folder + '.s3v'
        while jk_tag > 0:
            target_jk = ('jk_%s_%d_b.png' % (mid_4, jk_tag))
            if os.path.exists(music_path + target_jk):
                jk_path = music_path + target_jk
                break
            jk_tag -= 1

        # Process special tracks
        if ad_hoc:
            s3v_suf, new_name = ad_hoc
            if s3v_suf:
                s3v_path = music_path + music_folder + '_%s.s3v' % s3v_suf
            if new_name:
                name = new_name

        # Transportation
        valid_name = name.replace('/', ' ').replace('\\', ' ').replace(':', ' ').replace('*', ' ') \
            .replace('?', ' ').replace('\"', ' ').replace('<', ' ').replace('>', ' ').replace('|', ' ')
        valid_artist = artist.replace('/', ' ').replace('\\', ' ').replace(':', ' ').replace('*', ' ') \
            .replace('?', ' ').replace('\"', ' ').replace('<', ' ').replace('>', ' ').replace('|', ' ')
        wma_path = '%s%s/%s - %s.wma' % (self.des_dir, gen_name[version], valid_name, valid_artist)
        mp3_path = '%s%s/%s - %s.mp3' % (self.des_dir, gen_name[version], valid_name, valid_artist)
        self.wma_list.append(wma_path)
        if os.path.exists(mp3_path):
            return
        shutil.copyfile(s3v_path, wma_path)

        # Conversion
        os.chdir(self.des_dir + gen_name[version] + '/')
        os.system('ffmpeg  -i \"%s\" -f mp2 \"%s\"' % (wma_path, mp3_path))

        # Tagging
        audio = eyed3.load(mp3_path)
        audio.initTag()
        audio.tag.version = (2, 3, 0)
        audio.tag.artist = artist
        audio.tag.title = name
        audio.tag.album = gen_name[version]
        audio.tag.track_num = mid
        audio.tag.bpm = bpm_max
        audio.tag.release_date = '%s-%s-%s' % (date[:4], date[4:6], date[6:])
        audio.tag.album_artist = 'BEMANI'
        audio.tag.images.set(3, open(jk_path, 'rb').read(), 'image/png')
        audio.tag.save()

    def epilogue(self):
        for gen in gen_name:
            os.remove(self.des_dir + gen + '/ffmpeg.exe')
        for wma_path in self.wma_list:
            if os.path.exists(wma_path):
                os.remove(wma_path)


if __name__ == '__main__':

    _data_dir = get_user_path('Choose the "/content/data" folder')
    _des_dir = get_user_path('Choose the output path')

    cvt = Convertor(_data_dir, _des_dir)
    for music in cvt.music_map:
        cvt.process(music)

    cvt.process([709, '月光乱舞', 'P*Light', 186.00, '20151126', 3, 3], ad_hoc=['', ''])
    cvt.process([709, '月光乱舞', 'P*Light', 186.00, '20151126', 3, 4], ad_hoc=['4i', '月光乱舞 - Gravity Edit. - '])
    cvt.process([927, '極圏', 'cosMo VS dj TAKA', 207.00, '20161014', 3, 1], ad_hoc=['', ''])
    cvt.process([927, '極圏', 'cosMo VS dj TAKA', 207.00, '20161014', 3, 4], ad_hoc=['4i', '極圏 - Heavenly Edit - '])

    cvt.process([1148, 'TWO-TORIAL', 'BEMANI Sound Team "PHQUASE vs DJ TOTTO"', 213.00, '20171116', 4, 1],
                ad_hoc=['1n', 'TWO-TORIAL - Novice Edit - '])
    cvt.process([1148, 'TWO-TORIAL', 'BEMANI Sound Team "PHQUASE vs DJ TOTTO"', 213.00, '20171116', 4, 2],
                ad_hoc=['2a', 'TWO-TORIAL - Advance Edit - '])
    cvt.process([1148, 'TWO-TORIAL', 'BEMANI Sound Team "PHQUASE vs DJ TOTTO"', 213.00, '20171116', 4, 3],
                ad_hoc=['3e', 'TWO-TORIAL - Exhaust Edit - '])
    cvt.process([1148, 'TWO-TORIAL', 'BEMANI Sound Team "PHQUASE vs DJ TOTTO"', 213.00, '20171116', 4, 5],
                ad_hoc=['5m', 'TWO-TORIAL - Maximum Edit - '])

    cvt.process(
        [1758, 'Help me, ERINNNNNN!! #幻想郷ホロイズムver.', 'COOL&amp;CREATE × 宝鐘マリンと愉快な仲間たち', 190.00, '20210428', 6, 1],
        ad_hoc=['1n', 'Help me, ERINNNNNN!! #幻想郷ホロイズムver. - Pekora Usada, Miko Sakura, Shion Murasaki Edit - '])
    cvt.process(
        [1758, 'Help me, ERINNNNNN!! #幻想郷ホロイズムver.', 'COOL&amp;CREATE × 宝鐘マリンと愉快な仲間たち', 190.00, '20210428', 6, 2],
        ad_hoc=['2a', 'Help me, ERINNNNNN!! #幻想郷ホロイズムver. - Marine Houshou, Fubuki Shirakami, Rushia Uruha Edit - '])
    cvt.process(
        [1758, 'Help me, ERINNNNNN!! #幻想郷ホロイズムver.', 'COOL&amp;CREATE × 宝鐘マリンと愉快な仲間たち', 190.00, '20210428', 6, 3],
        ad_hoc=['3e', 'Help me, ERINNNNNN!! #幻想郷ホロイズムver. - Marine Houshou, Matsuri Natsuiro, Aqua Minato Edit - '])
    cvt.process(
        [1758, 'Help me, ERINNNNNN!! #幻想郷ホロイズムver.', 'COOL&amp;CREATE × 宝鐘マリンと愉快な仲間たち', 190.00, '20210428', 6, 5],
        ad_hoc=['5m', 'Help me, ERINNNNNN!! #幻想郷ホロイズムver. - Noel Shirogane, Flare Shiranui Edit - '])

    cvt.epilogue()
