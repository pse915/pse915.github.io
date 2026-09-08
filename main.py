import pygame
import sys
import asyncio
import json
import math
import random
import urllib.request

try:
    from platform import window
except ImportError:
    window = None

pygame.init()

WIDTH, HEIGHT = 960, 540
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("가족 의사소통 & 갈등 해결 마스터")

# 파스텔 톤 색상 팔레트
BG_COLOR = (245, 247, 250)
PRIMARY = (129, 140, 248)
PRIMARY_DARK = (79, 70, 229)
ACCENT_PINK = (251, 113, 133)
ACCENT_GREEN = (52, 211, 153)
CARD_BG = (255, 255, 255)
CARD_BORDER = (224, 231, 255)
TEXT_DARK = (30, 41, 59)
TEXT_MUTED = (148, 163, 184)
WHITE = (255, 255, 255)
ERROR_RED = (248, 113, 113)
GOLD_YELLOW = (251, 191, 36)

FONT_TITLE = None
FONT_SUB = None
FONT_BODY = None

def get_font(size, bold=False):
    try:
        return pygame.font.Font("font.ttf", size)
    except Exception:
        return pygame.font.Font(None, size)

# ================= 파티클 시스템 =================
particles = []

class FloatingParticle:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.alpha = 255

    def update(self):
        self.y -= 1.5
        self.alpha -= 5
        return self.alpha > 0

    def draw(self, surface):
        if FONT_SUB:
            txt_sf = FONT_SUB.render(self.text, True, self.color)
            txt_sf.set_alpha(self.alpha)
            surface.blit(txt_sf, (self.x - txt_sf.get_width()//2, self.y))

def add_hearts(x, y):
    for _ in range(6):
        particles.append(FloatingParticle(x + random.randint(-40, 40), y + random.randint(-20, 20), "💖", ACCENT_PINK))

def add_sweat(x, y):
    for _ in range(4):
        particles.append(FloatingParticle(x + random.randint(-40, 40), y + random.randint(-20, 20), "💦", PRIMARY))

# ================= 대형 생동감 캐릭터 아바타 (몸통+애니메이션) =================
def draw_avatar(surface, x, y, role="sister", expression="happy", bounce_offset=0, ticks=0):
    y += int(bounce_offset)
    
    # 캐릭터 기우뚱 애니메이션
    tilt_angle = math.sin(ticks * 0.004) * 3
    
    # 눈 blink 계산
    is_blinking = (ticks % 3000) < 150

    # 역할별 스킨 & 의상 색상
    role_colors = {
        "sister": ((254, 226, 226), (244, 114, 182), (194, 65, 12)),  # 피부, 옷, 머리
        "brother": ((254, 243, 199), (96, 165, 250), (30, 41, 59)),
        "dad": ((253, 230, 138), (71, 85, 105), (51, 65, 85)),
        "mom": ((254, 243, 199), (167, 139, 250), (120, 53, 15))
    }
    skin_col, cloth_col, hair_col = role_colors.get(role, role_colors["sister"])

    # 1. 캐릭터 그림자
    pygame.draw.ellipse(surface, (218, 224, 233), (x - 45, y + 65, 90, 16))

    # 2. 상체/의상 (어깨 라인)
    pygame.draw.ellipse(surface, cloth_col, (x - 42, y + 15, 84, 60))
    pygame.draw.rect(surface, skin_col, (x - 14, y + 10, 28, 20), border_radius=6) # 목

    # 3. 머리 윤곽 (대형 크기 R=46)
    pygame.draw.circle(surface, skin_col, (x, y - 10), 46)
    pygame.draw.circle(surface, (251, 146, 60), (x, y - 10), 46, 2)

    # 4. 볼터치
    pygame.draw.circle(surface, (251, 113, 133, 120), (x - 24, y), 9)
    pygame.draw.circle(surface, (251, 113, 133, 120), (x + 24, y), 9)

    # 5. 역할별 헤어 스타일
    if role == "sister":
        pygame.draw.circle(surface, hair_col, (x - 40, y - 18), 16) # 양갈래 머리
        pygame.draw.circle(surface, hair_col, (x + 40, y - 18), 16)
        pygame.draw.arc(surface, hair_col, (x - 48, y - 58, 96, 60), 0, 3.14, 16)
    elif role == "brother":
        pygame.draw.arc(surface, hair_col, (x - 48, y - 60, 96, 50), 0, 3.14, 18) # 숏컷
    elif role == "dad":
        pygame.draw.rect(surface, hair_col, (x - 46, y - 54, 92, 26), border_radius=12)
        # 안경
        pygame.draw.circle(surface, (30, 41, 59), (x - 16, y - 14), 12, 2)
        pygame.draw.circle(surface, (30, 41, 59), (x + 16, y - 14), 12, 2)
        pygame.draw.line(surface, (30, 41, 59), (x - 4, y - 14), (x + 4, y - 14), 2)
    elif role == "mom":
        pygame.draw.circle(surface, hair_col, (x, y - 56), 20) # 올림머리
        pygame.draw.arc(surface, hair_col, (x - 50, y - 56, 100, 60), 0, 3.14, 16)

    # 6. 표정 및 눈동자 애니메이션
    if expression == "sad":
        # 슬픈 눈 > <
        pygame.draw.line(surface, TEXT_DARK, (x - 22, y - 18), (x - 10, y - 12), 3)
        pygame.draw.line(surface, TEXT_DARK, (x - 10, y - 12), (x - 22, y - 6), 3)
        pygame.draw.line(surface, TEXT_DARK, (x + 22, y - 18), (x + 10, y - 12), 3)
        pygame.draw.line(surface, TEXT_DARK, (x + 10, y - 12), (x + 22, y - 6), 3)
        # 시무룩 입
        pygame.draw.arc(surface, TEXT_DARK, (x - 12, y + 8, 24, 14), 0, 3.14, 3)
    elif expression == "angry":
        # 분노 눈썹 \ /
        pygame.draw.line(surface, ERROR_RED, (x - 24, y - 24), (x - 8, y - 16), 4)
        pygame.draw.line(surface, ERROR_RED, (x + 24, y - 24), (x + 8, y - 16), 4)
        pygame.draw.circle(surface, TEXT_DARK, (x - 14, y - 12), 4)
        pygame.draw.circle(surface, TEXT_DARK, (x + 14, y - 12), 4)
        # 입 모양
        pygame.draw.line(surface, TEXT_DARK, (x - 12, y + 10), (x + 12, y + 10), 3)
        # 분노 마크
        txt_sf = FONT_SUB.render("💢", True, ERROR_RED)
        surface.blit(txt_sf, (x + 26, y - 50))
    else: # happy / normal
        if is_blinking:
            pygame.draw.line(surface, TEXT_DARK, (x - 20, y - 14), (x - 8, y - 14), 3)
            pygame.draw.line(surface, TEXT_DARK, (x + 8, y - 14), (x + 20, y - 14), 3)
        else:
            pygame.draw.circle(surface, TEXT_DARK, (x - 14, y - 14), 5)
            pygame.draw.circle(surface, WHITE, (x - 16, y - 16), 2)
            pygame.draw.circle(surface, TEXT_DARK, (x + 14, y - 14), 5)
            pygame.draw.circle(surface, WHITE, (x + 12, y - 16), 2)
        # 웃는 입
        pygame.draw.arc(surface, ACCENT_PINK, (x - 14, y - 2, 28, 18), 3.14, 6.28, 3)

# ================= 말풍선 (크기 및 시각적 강조) =================
def draw_speech_bubble(surface, text, x, y, w, h):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, CARD_BG, rect, border_radius=18)
    pygame.draw.rect(surface, PRIMARY, rect, 3, border_radius=18)
    
    # 꼬리표
    points = [(x - 16, y + 36), (x, y + 24), (x, y + 48)]
    pygame.draw.polygon(surface, CARD_BG, points)
    pygame.draw.lines(surface, PRIMARY, False, [(x, y + 24), (x - 16, y + 36), (x, y + 48)], 3)

    words = text.split('\n')
    for i, line in enumerate(words):
        txt_sf = FONT_SUB.render(line, True, TEXT_DARK)
        surface.blit(txt_sf, (x + 22, y + 16 + i * 26))

# ================= 모션 버튼 & 입력창 =================
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.hover = False

    def draw(self, surface):
        press_offset = 3 if self.hover else 0
        
        shadow_rect = pygame.Rect(self.rect.x, self.rect.y + 4, self.rect.w, self.rect.h)
        pygame.draw.rect(surface, (203, 213, 225), shadow_rect, border_radius=10)

        draw_rect = pygame.Rect(self.rect.x, self.rect.y + press_offset, self.rect.w, self.rect.h)
        bg = PRIMARY if self.hover else CARD_BG
        border = PRIMARY_DARK if self.hover else CARD_BORDER
        text_color = WHITE if self.hover else TEXT_DARK

        pygame.draw.rect(surface, bg, draw_rect, border_radius=10)
        pygame.draw.rect(surface, border, draw_rect, 2, border_radius=10)

        txt_sf = FONT_BODY.render(self.text, True, text_color)
        txt_rect = txt_sf.get_rect(center=draw_rect.center)
        surface.blit(txt_sf, txt_rect)

    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

class InputBox:
    def __init__(self, x, y, w, h, placeholder=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.placeholder = placeholder
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < 15 and event.unicode.isprintable():
                self.text += event.unicode

    def draw(self, surface):
        color = PRIMARY if self.active else CARD_BORDER
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=8)
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=8)
        
        disp_text = self.text if self.text else self.placeholder
        text_color = TEXT_DARK if self.text else TEXT_MUTED
        txt_sf = FONT_BODY.render(disp_text, True, text_color)
        surface.blit(txt_sf, (self.rect.x + 12, self.rect.y + 8))

# ================= 100% 가족 관련 질문 데이터베이스 =================
QUESTIONS = [
    {
        "cat": "1단계: 나-전달법 (행동 묘사)", "role": "sister", "exp": "angry",
        "dialogue": "동생이 허락 없이 학용품을 가져가 잃어버린 상황!",
        "q": "비난이나 평가 없이 상대방의 '행동'만 객관적으로 표현한 것은?",
        "options": [
            ("1. 너는 왜 매번 허락도 없이 남의 물건을 마음대로 건드리니?", False),
            ("2. 내 허락 없이 필통에서 학용품을 가져가서 잃어버렸어.", True),
            ("3. 넌 항상 정리정돈도 안 하고 무책임한 태도를 보이더라.", False),
            ("4. 남의 물건을 몰래 가져가는 건 정말 나쁜 행동이야.", False),
            ("5. 네가 자꾸 내 물건을 건드리니까 내가 항상 화가 나는 거야.", False)
        ]
    },
    {
        "cat": "2단계: 나-전달법 (영향 및 감정)", "role": "brother", "exp": "sad",
        "dialogue": "형(누나)이 약속 시간에 30분 넘게 연락도 없이 늦게 온 상황!",
        "q": "나에게 미친 '영향과 솔직한 감정'을 올바르게 표현한 것은?",
        "options": [
            ("1. 오랫동안 혼자 기다리면서 걱정되고 내 시간이 허비되어 속상했어.", True),
            ("2. 너 진짜 시간 개념이 없구나. 약속을 왜 하자고 했니?", False),
            ("3. 너 때문에 오늘 내 하루 기분을 완전히 다 망쳐버렸어.", False),
            ("4. 다음부터 늦으면 나도 똑같이 늦게 나갈 테니 알아서 해.", False),
            ("5. 약속 하나 제대로 못 지키면서 무슨 중요한 일을 하겠다는 거니?", False)
        ]
    },
    {
        "cat": "3단계: 나-전달법 (바라는 사항)", "role": "dad", "exp": "sad",
        "dialogue": "부모님이 내 의견을 묻지 않고 주말 일정을 일방적으로 정하셨을 때!",
        "q": "상대방에게 올바르게 '바라는 사항'을 요청하는 문장은?",
        "options": [
            ("1. 부모님 마음대로 하실 거면 앞으로 저한테 아무것도 묻지 마세요.", False),
            ("2. 제 일정과 의견도 먼저 물어봐 주시고 함께 결정해 주셨으면 좋겠어요.", True),
            ("3. 이번 결정 취소 안 해주시면 저 주말에 집 나가서 안 들어올 거예요.", False),
            ("4. 제발 저 좀 그만 괴롭히시고 그냥 제 일에 신경 꺼주세요.", False),
            ("5. 부모님의 결정 방식은 완전히 잘못되었으니 당장 수정해 주세요.", False)
        ]
    },
    {
        "cat": "4단계: 너-전달법 → 나-전달법 변환", "role": "sister", "exp": "angry",
        "dialogue": "너-전달법: \"너는 왜 내가 말할 때마다 폰만 보고 딴청이니?\"",
        "q": "위 '너-전달법'을 올바른 '나-전달법'으로 바꾼 것은?",
        "options": [
            ("1. 폰 좀 그만 보고 사람 얼굴을 보며 대화하는 예의를 갖춰라.", False),
            ("2. 내가 말할 때 스마트폰을 보면 내 말을 경청받지 못하는 느낌이 들어 서운해.", True),
            ("3. 너는 스마트폰 중독이라 사람과 제대로 된 대화가 불가능하구나.", False),
            ("4. 앞으로 대화할 때는 네 스마트폰을 전부 압수해야겠어.", False),
            ("5. 내가 말하는데 폰을 계속 보면 너랑 다시는 대화 안 할 거야.", False)
        ]
    },
    {
        "cat": "5단계: 나-전달법 3요소 완성", "role": "brother", "exp": "happy",
        "dialogue": "\"네가 연락 없이 약속에 늦어서(행동), 기다리며 걱정되고 속상했어(영향/감정).\"",
        "q": "이 문장 뒤에 이어질 마지막 '바라는 사항'으로 가장 적절한 것은?",
        "options": [
            ("1. 앞으로는 늦을 것 같으면 미리 나에게 연락을 해주면 좋겠어.", True),
            ("2. 다음부터 한 번만 더 늦으면 너랑 다시는 안 놀아.", False),
            ("3. 너도 똑같이 30분 동안 길거리에서 기다려 봐야 정신 차리지?", False),
            ("4. 앞으로 너와의 모든 일정은 내가 전부 취소하도록 할게.", False),
            ("5. 늦은 시간만큼 네가 맛있는 걸 사서 정식으로 사과하면 좋겠어.", False)
        ]
    },
    {
        "cat": "6단계: 경청과 공감", "role": "mom", "exp": "sad",
        "dialogue": "가족 구성원이 시험이나 일로 마음처럼 되지 않아 우울하다고 고민할 때!",
        "q": "경청과 공감의 바람직한 대화 태도는 무엇일까요?",
        "options": [
            ("1. 상대방의 평소 생활 습관과 잘못된 점을 즉시 지적해 준다.", False),
            ("2. 말하는 중간에 개입하여 나의 더 안 좋았던 경험담을 이야기한다.", False),
            ("3. 비판이나 성급한 조언 전에 상대방이 느꼈을 좌절감에 먼저 공감해 준다.", True),
            ("4. 별일 아니라는 듯 대수롭지 않게 넘기며 빠르게 주제를 바꾼다.", False),
            ("5. 해결책을 제시하기 위해 상대방의 말을 끊고 논리적으로 질문한다.", False)
        ]
    },
    {
        "cat": "7단계: 나-전달법과 비언어적 표현", "role": "sister", "exp": "angry",
        "dialogue": "나-전달법으로 말하지만 표정은 찌푸리고 팔짱을 끼고 있는 상황!",
        "q": "나-전달법을 사용할 때 비언어적 표현(표정, 말투, 시선)의 올바른 태도는?",
        "options": [
            ("1. 말의 내용보다 상대를 제압하는 강한 눈빛과 억양이 중요하다.", False),
            ("2. 말만 나-전달법으로 한다면 비꼬는 말투나 표정은 상관없다.", False),
            ("3. 진정성 전달을 위해 언어적 메시지와 비언어적 표현을 일치시켜야 한다.", True),
            ("4. 감정을 숨기기 위해 무표정한 얼굴과 기계적인 목소리를 유지한다.", False),
            ("5. 상대방이 미안함을 느끼도록 가벼운 한숨을 쉬며 말하는 것이 좋다.", False)
        ]
    },
    {
        "cat": "8단계: 성격 유형별 대화 (사고형 T)", "role": "dad", "exp": "happy",
        "dialogue": "원칙과 논리적 사실 관계를 중시하는 '사고형(T)' 아빠와의 대화!",
        "q": "T형 가족 구성원과 갈등을 해결할 때 가장 효과적인 대화법은?",
        "options": [
            ("1. 감정적으로 눈물을 흘리며 내 기분만 알아달라고 호소한다.", False),
            ("2. 객관적인 사실과 이유를 차분하고 논리적으로 설명한다.", True),
            ("3. 상대방의 논리적 오류를 계속 지적하며 언쟁에서 이기려 한다.", False),
            ("4. 논리적인 대화는 무의미하므로 대화를 완전히 포기한다.", False),
            ("5. 상대방의 서운한 점을 지적하며 감정적인 대답을 강요한다.", False)
        ]
    },
    {
        "cat": "9단계: 성격 유형별 대화 (감정형 F)", "role": "sister", "exp": "sad",
        "dialogue": "관계와 공감, 마음의 공유를 중시하는 '감정형(F)' 동생과의 대화!",
        "q": "F형 가족 구성원의 마음을 열 수 있는 바람직한 대화법은?",
        "options": [
            ("1. 옳고 그름을 따지기 전에 상대방이 느꼈을 감정과 입장을 인정해 준다.", True),
            ("2. 상대방의 감정은 비이성적이라며 차갑게 사실만 지적한다.", False),
            ("3. 감정적인 이야기에는 응하지 않고 빠른 해결책만 제시한다.", False),
            ("4. 동조해 주는 척하면서 은근히 상대방의 잘못을 깨닫게 한다.", False),
            ("5. 상대방의 감정 표현을 장난으로 넘기며 분위기를 전환한다.", False)
        ]
    },
    {
        "cat": "10단계: 가족 갈등 해결 4단계", "role": "mom", "exp": "happy",
        "dialogue": "가족 회의에서 갈등을 올바르게 해결하는 체계적인 4단계 프로세스!",
        "q": "가족 갈등을 해결하는 올바른 순서로 가장 적절한 것은?",
        "options": [
            ("1. 갈등 확인 → 해결 방법 탐색 → 해결 방법 결정 → 실행 및 평가", True),
            ("2. 해결 방법 결정 → 갈등 확인 → 실행 및 평가 → 해결 방법 탐색", False),
            ("3. 갈등 확인 → 실행 및 평가 → 해결 방법 탐색 → 해결 방법 결정", False),
            ("4. 해결 방법 탐색 → 갈등 확인 → 해결 방법 결정 → 실행 및 평가", False),
            ("5. 갈등 확인 → 해결 방법 결정 → 해결 방법 탐색 → 실행 및 평가", False)
        ]
    }
]

# ================= 구글 시트 전송 함수 (최종 수정 완료) =================
def submit_to_google_sheet(std_id, name, score):
    script_url = "https://script.google.com/macros/s/AKfycbz2z7ozmBNDNvLu_LtXwt5jlN5AjxtbLGB2_fdLhkJVe5To1qyptJ_T_rF7vV1A2Pmt/exec" 
    data_dict = {"std_id": std_id, "name": name, "score": score}
    payload = json.dumps(data_dict).encode('utf-8')

    # 1. 웹 브라우저 실행 환경 (Pygbag)
    if window:
        try:
            # text/plain으로 전송해야 CORS Preflight(OPTIONS) 차단을 피할 수 있음
            window.fetch(script_url, {
                'method': 'POST',
                'headers': {'Content-Type': 'text/plain'},
                'body': json.dumps(data_dict),
                'mode': 'no-cors'
            })
            return True
        except Exception as e:
            print("Web Fetch Error:", e)
            return False

    # 2. 일반 PC 파이썬 실행 환경 (urllib)
    else:
        try:
            req = urllib.request.Request(
                script_url, 
                data=payload, 
                headers={
                    'Content-Type': 'text/plain;charset=utf-8',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                },
                method='POST'
            )
            with urllib.request.urlopen(req) as response:
                print("PC 제출 완료, 응답 코드:", response.getcode())
            return True
        except Exception as e:
            print("PC Submit Error:", e)
            return False

# ================= 메인 실행 루프 =================
async def main():
    global FONT_TITLE, FONT_SUB, FONT_BODY
    await asyncio.sleep(0.1)
    
    FONT_TITLE = get_font(22, bold=True)
    FONT_SUB = get_font(16, bold=True)
    FONT_BODY = get_font(14)

    clock = pygame.time.Clock()
    
    q_idx = 0
    score = 0
    combo = 0
    shake_amount = 0
    feedback_msg = ""
    feedback_color = ACCENT_GREEN

    id_input = InputBox(330, 260, 300, 36, "예: 10101")
    name_input = InputBox(330, 315, 300, 36, "예: 홍길동")
    submit_btn = Button(380, 375, 200, 40, "구글 시트에 제출")
    submitted = False

    buttons = []
    def load_question():
        nonlocal buttons
        buttons = []
        opts = QUESTIONS[q_idx]["options"]
        for idx, (text, is_correct) in enumerate(opts):
            btn = Button(40, 275 + idx * 46, 880, 38, text)
            buttons.append((btn, is_correct))

    load_question()
    running = True

    while running:
        ticks = pygame.time.get_ticks()
        bounce_offset = math.sin(ticks * 0.006) * 5
        
        shake_x = random.randint(-shake_amount, shake_amount) if shake_amount > 0 else 0
        shake_y = random.randint(-shake_amount, shake_amount) if shake_amount > 0 else 0
        if shake_amount > 0: shake_amount -= 1

        canvas = pygame.Surface((WIDTH, HEIGHT))
        canvas.fill(BG_COLOR)
        pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if q_idx < 10:
                for btn, is_correct in buttons:
                    btn.check_hover(pos)
                    if event.type == pygame.MOUSEBUTTONDOWN and btn.rect.collidepoint(pos):
                        if is_correct:
                            combo += 1
                            score += 10
                            shake_amount = 0
                            feedback_msg = f"🎉 정답! 가족 화목도 UP! ({combo}연속 성공!)"
                            feedback_color = ACCENT_GREEN
                            add_hearts(100, 140)
                        else:
                            combo = 0
                            shake_amount = 8
                            feedback_msg = "💔 오답! 상처주는 대화법입니다."
                            feedback_color = ERROR_RED
                            add_sweat(100, 140)
                        
                        q_idx += 1
                        if q_idx < 10:
                            load_question()
                        break
            else:
                id_input.handle_event(event)
                name_input.handle_event(event)
                submit_btn.check_hover(pos)
                
                if event.type == pygame.MOUSEBUTTONDOWN and submit_btn.rect.collidepoint(pos) and not submitted:
                    if id_input.text and name_input.text:
                        success = submit_to_google_sheet(id_input.text, name_input.text, score)
                        if success:
                            submitted = True
                            feedback_msg = "✨ 성공적으로 결과가 제출되었습니다!"
                            feedback_color = ACCENT_GREEN
                        else:
                            feedback_msg = "전송 실패! 인터넷 연결을 확인해 주세요."
                            feedback_color = ERROR_RED
                    else:
                        feedback_msg = "학번과 이름을 입력해 주세요!"
                        feedback_color = ERROR_RED

        # 상단 헤더 & 화목도 게이지
        pygame.draw.rect(canvas, PRIMARY, (0, 0, WIDTH, 54))
        title_txt = FONT_TITLE.render("가족 의사소통 & 갈등 해결 마스터", True, WHITE)
        canvas.blit(title_txt, (20, 14))
        
        pygame.draw.rect(canvas, CARD_BORDER, (WIDTH - 250, 15, 210, 24), border_radius=12)
        gauge_width = int((score / 100) * 206)
        if gauge_width > 0:
            pygame.draw.rect(canvas, ACCENT_PINK, (WIDTH - 248, 17, gauge_width, 20), border_radius=10)
        
        gauge_txt = FONT_BODY.render(f"가족 화목도 {score}%", True, WHITE)
        canvas.blit(gauge_txt, (WIDTH - 185, 18))

        if q_idx < 10:
            q_data = QUESTIONS[q_idx]

            # 카테고리
            cat_txt = FONT_SUB.render(f"STAGE {q_idx+1}. {q_data['cat']}", True, PRIMARY_DARK)
            canvas.blit(cat_txt, (40, 64))

            # 대형 캐릭터 (좌측 배치) & 말풍선 (우측 배치)
            draw_avatar(canvas, 100, 145, role=q_data["role"], expression=q_data["exp"], bounce_offset=bounce_offset, ticks=ticks)
            draw_speech_bubble(canvas, q_data["dialogue"], 190, 95, 730, 80)

            # 질문 문항 텍스트
            q_txt = FONT_SUB.render(q_data["q"], True, TEXT_DARK)
            canvas.blit(q_txt, (40, 240))

            # 선택 버튼 출력
            for btn, _ in buttons:
                btn.draw(canvas)

            if combo > 1:
                combo_txt = FONT_SUB.render(f"🔥 {combo} COMBO!", True, GOLD_YELLOW)
                canvas.blit(combo_txt, (WIDTH - 130, 64))

        else: # 결과 페이지
            pygame.draw.rect(canvas, WHITE, (180, 85, 600, 360), border_radius=16)
            pygame.draw.rect(canvas, PRIMARY, (180, 85, 600, 360), 3, border_radius=16)

            res_title = FONT_TITLE.render("🏆 학습 완료! 결과를 제출하세요", True, PRIMARY_DARK)
            canvas.blit(res_title, (WIDTH//2 - res_title.get_width()//2, 115))

            final_score_txt = FONT_SUB.render(f"최종 가족 화목도: {score}점 / 100점", True, TEXT_DARK)
            canvas.blit(final_score_txt, (WIDTH//2 - final_score_txt.get_width()//2, 160))

            lbl_id = FONT_BODY.render("학번:", True, TEXT_DARK)
            lbl_name = FONT_BODY.render("이름:", True, TEXT_DARK)
            canvas.blit(lbl_id, (270, 268))
            canvas.blit(lbl_name, (270, 323))

            id_input.draw(canvas)
            name_input.draw(canvas)
            
            if not submitted:
                submit_btn.draw(canvas)
            else:
                done_txt = FONT_TITLE.render("✓ 성공적으로 제출되었습니다!", True, ACCENT_GREEN)
                canvas.blit(done_txt, (WIDTH//2 - done_txt.get_width()//2, 385))

        # 파티클 업데이트
        for p in particles[:]:
            p.draw(canvas)
            if not p.update():
                particles.remove(p)

        # 피드백 메세지
        if feedback_msg:
            fb_txt = FONT_BODY.render(feedback_msg, True, feedback_color)
            canvas.blit(fb_txt, (WIDTH//2 - fb_txt.get_width()//2, 510))

        screen.blit(canvas, (shake_x, shake_y))
        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
