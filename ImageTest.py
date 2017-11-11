# coding: utf-8

"""pygameアプリ補助ツール ImageTest0.2
imageフォルダ内の画像を全部表示する。
画像を選択し、配置し、その座標を見て、そのデータをテキスト出力できる。
以上の操作はマウスですべて出来るし、キーボードでもすべて出来る。

0.1からの変更点
●imageフォルダの画像を全部読むので、スクリプトで画像を設定する必要がなくなった。
●選択した画像を最前面に表示するようになった。
●マウス操作に対応した。
●現在の状態をテキスト出力できるようになった。

========================================
バージョン0.2(2016-08-01)
    上述の通り完成。
バージョン1.0(2017-09-25)
    macのためにマウスクリック2をF1に変換するのを追加。
    docをつけました。
"""

import sys
import os
import pygame
import imghdr
from pygame.locals import *

# ショートカットからの実行だったらカレントディレクトリをexeのあるディレクトリに移す。
for d in ['image', 'other']:
    if not os.path.exists(d):
        os.chdir(os.path.dirname(sys.executable))


class Images:
    """画像のサーフィスと座標をもつクラス。
    property
        name 画像名
        surface サーフィス
        xy 座標
    """

    def __init__(self, imagePath, transparence=False):
        self.name = os.path.basename(imagePath)
        self.surface = self.createSurface(imagePath, transparence)
        self.xy = [0, 0]
        # 画像の表示状態をimageOrderリストで管理するようになったら必要なくなった
        # self.put = False

    def createSurface(self, imagePath, transparence):
        """画像サーフィスを作成する。"""
        if transparence == False:
            return pygame.image.load(imagePath).convert_alpha()
        else:
            surface = pygame.image.load(imagePath).convert_alpha()
            surface.set_colorkey(surface.get_at(transparence), RLEACCEL)
            return surface

    def blit(self):
        """画面にblitする。"""
        return screen.blit(self.surface, self.xy)

class ImageTest:
    def __init__(self):
        pass

    def main(self):
        """ゲームループのあるメソッド。"""
        package = {
            'imageList': self.createImageList(),
            'mode': 'select',
            'num': 0,
        }
        # 長押しを有効化する。間隔はselectに合わせる
        pygame.key.set_repeat(1, 500)

        while True:
            screen.fill((0,0,0))

            # 画像を置く
            for instance in package['imageList']:
                screen.blit(instance.surface, tuple(instance.xy))

            # 画像選択モードと画像配置モード
            if package['mode'] == 'select':
                package = self.selectMode(package)
            elif package['mode'] == 'place':
                package = self.placeMode(package)
            elif package['mode'].endswith('__putfile'):
                package = self.putfileMode(package)

            pygame.display.update()
            clock.tick(framerate)

    def createImageList(self):
        """imageフォルダの画像を全部Imagesインスタンスにしてリストを作る。"""
        imageList = []
        files = os.listdir('image')
        for file in files:
            # まずは画像じゃなかったらインスタンスにはしない
            imageType = imghdr.what('image/' + file)
            if imageType not in ['jpeg', 'png', 'gif', 'bmp']:
                continue
            imageList.append(Images('image/' + file))
        return imageList

    def blitText(self, textList):
        """Rect作ってその上にtext載せる"""
        # メッセージボックスの大きさを求める (一番長い行の幅+10, フォントの高さ*行数+10)
        width = 0
        for line in textList:
            textSize = font.size(line)
            width = textSize[0] if width < textSize[0] else width
        width += 10
        height = textSize[1] * len(textList) + 10
        # 右上にRect配置
        pygame.draw.rect(screen, (255,255,255),
            Rect(screenSize[0]-width-5, 5, width, height))
        # テキストを置く
        lineNum = 0
        for line in textList:
            text = font.render(line, True, (0,0,0))
            screen.blit(text, (screenSize[0]-width, 10+font.get_linesize()*lineNum))
            lineNum += 1

    def selectMode(self, package):
        """画像選択モード
        上下:選択
        Z:画像配置モードへ
        """
        # 右上にテキスト表示する
        text1 = '<選択モード> ﾏｳｽﾎｲｰﾙ:画像選択 左ｸﾘｯｸ:決定 F1:ﾃｷｽﾄ出力'
        text2 = '▼ ' + package['imageList'][package['num']].name
        text3 = '  位置: ' + str(package['imageList'][package['num']].xy)
        self.blitText([text1, text2, text3])

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_F4 and bool(event.mod and KMOD_ALT):
                    sys.exit()
                if event.key == K_ESCAPE:
                    sys.exit()
                if event.key == K_F1:
                    self.putfile(package)
                    package['mode'] = package['mode'] + '__putfile'
                num = package['num']
                if event.key == K_UP:
                    package['num'] = num-1 if num != 0 else len(package['imageList'])-1
                if event.key == K_DOWN:
                    package['num'] = num+1 if num != len(package['imageList'])-1 else 0
                if event.key == K_z:
                    package = self.changeImageOrder(package)
                    package['mode'] = 'place'
            if event.type == MOUSEBUTTONDOWN:
                num = package['num']
                # 左クリック
                if event.button == 1:
                    package = self.changeImageOrder(package)
                    package['mode'] = 'place'
                # マウスホイール上下
                if event.button == 4:
                    package['num'] = num+1 if num != len(package['imageList'])-1 else 0
                if event.button == 5:
                    package['num'] = num-1 if num != 0 else len(package['imageList'])-1
                # F1の代替。
                if event.button == 2:
                    self.putfile(package)
                    package['mode'] = package['mode'] + '__putfile'
        return package

    def changeImageOrder(self, package):
        """現在選択されてる画像をリストの最後(最前面)にもってくる。
        背景画像が前面に出てしまったときの対策。"""
        selected = package['imageList'][package['num']]
        del package['imageList'][package['num']]
        package['imageList'].append(selected)
        package['num'] = len(package['imageList']) - 1
        return package

    def placeMode(self, package):
        """画像配置モード
        マウスクリック:その座標に配置
        X:画像選択モードへ
        """
        # 右上にテキスト表示する
        text1 = '<配置ﾓｰﾄﾞ> 左ﾄﾞﾗｯｸﾞ:画像配置 右ｸﾘｯｸ:戻る F1:ﾃｷｽﾄ出力'
        text2 = '  ' + package['imageList'][package['num']].name
        text3 = '▼ 位置: ' + str(package['imageList'][package['num']].xy)
        self.blitText([text1, text2, text3])

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_F4 and bool(event.mod and KMOD_ALT):
                    sys.exit()
                if event.key == K_ESCAPE:
                    sys.exit()
                if event.key == K_F1:
                    self.putfile(package)
                    package['mode'] = package['mode'] + '__putfile'
                if event.key == K_x:
                    package['mode'] = 'select'
                # 上下左右で画像移動
                x = package['imageList'][package['num']].xy[0]
                y = package['imageList'][package['num']].xy[1]
                if event.key == K_UP:
                    package['imageList'][package['num']].xy[1] = y-1 if y != 0 else y
                if event.key == K_DOWN:
                    package['imageList'][package['num']].xy[1] = y+1 if y != screenSize[0] else y
                if event.key == K_LEFT:
                    package['imageList'][package['num']].xy[0] = x-1 if x != 0 else x
                if event.key == K_RIGHT:
                    package['imageList'][package['num']].xy[0] = x+1 if x != screenSize[1] else x
            # マウスドラッグ(左)でも画像移動
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                package['imageList'][package['num']].xy = [pos[0], pos[1]]
            # マウスクリック(右)で戻る
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3:
                    package['mode'] = 'select'
                # F1の代替。
                if event.button == 2:
                    self.putfile(package)
                    package['mode'] = package['mode'] + '__putfile'
        return package

    def putfile(self, package):
        """画像の一覧をテキスト出力する。"""
        text = ''
        for instance in package['imageList']:
            text += instance.name + ' ' + str(instance.xy) + '\n'
        with open('imagetestText.txt', encoding='SJIS', mode='w') as f:
            f.write(text)

    def putfileMode(self, package):
        """入力があるまで「テキスト出力しました」を表示する。"""
        text0 = '● データをテキスト出力しました ●'
        text1 = '  何かキーを押してください'
        self.blitText([text0, text1])

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                # rstripは'select'を'selec'にするのでreplaceを使う
                package['mode'] = package['mode'].replace('__putfile', '')
        return package

if __name__ == '__main__':
    pygame.init()
    screenSize = (640, 480)
    screen = pygame.display.set_mode(screenSize)
    icon = pygame.image.load('other/pythongreen32x32.png').convert_alpha()
    icon.set_colorkey(icon.get_at((0,0)), RLEACCEL)
    pygame.display.set_icon(icon)
    pygame.display.set_caption('画像配置テスト ESCキーで終了できます')
    font = pygame.font.Font('other/VL-Gothic-Regular.ttf', 12)
    clock = pygame.time.Clock()
    framerate = 20

    instance = ImageTest()
    instance.main()