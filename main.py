import pygame
import sys
import asyncio
import json

# 웹(Pygbag) 환경에서의 js fetch 지원 체크
try:
    from platform import window
except ImportError:
    window = None

# Pygame 초기화
pygame.init()

# 화면 설정 (960x540 / 16:9)
WIDTH, HEIGHT = 960, 540
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("가족 의사소통 & 갈등 해결 마스터")

# 색상 파렛트 (파스텔 & 교과서 톤)
BG_COLOR = (240, 244, 248)
PRIMARY = (99, 102, 241)       # 보라 파랑
PRIMARY_DARK = (67, 56, 202)
ACCENT_PINK = (244, 114, 182)   # 핑크 강조
ACCENT_GREEN = (52, 211, 153)  # 정답 녹색
CARD_BG = (255, 255, 255)
CARD_BORDER = (226, 232, 240)
TEXT_DARK = (30, 41, 59)
TEXT_MUTED = (100, 116, 139)
WHITE = (255, 255, 255)
ERROR_RED = (248, 113, 113)

# 폰트 로드
def get_font(size, bold=False):
    try:
        return pygame.font.Font("NanumGothic.ttf", size)
    except:
        return pygame.font.SysFont("malgungothic", size, bold=bold)

FONT_TITLE = get_font(24, bold=True)
FONT_SUB = get_font(18, bold=True)
FONT_BODY = get_font(16)
FONT_SMALL = get_font(14)

# ================= 귀여운 캐릭터 & 말풍선 그리기 함수 =================
def draw_avatar(surface, x, y, role="friend", expression="happy"):
    # 얼굴 바탕
    face_color = (254, 226, 226) if role == "sister" else ((253, 230, 138) if role == "dad" else (254, 243, 199))
    pygame.draw.circle(surface, face_color, (x, y), 35)
    pygame.draw.circle(surface, (217, 119, 6), (x, y), 35, 2)

    # 머리 스타일
    if role == "sister": # 머리 묶음
        pygame.draw.circle(surface, (180, 83, 9), (x - 25, y - 10), 12)
        pygame.draw.circle(surface, (180, 83, 9), (x + 25, y - 10), 12)
        pygame.draw.arc(surface, (180, 83, 9), (x - 35, y - 40, 70, 50), 0, 3.14, 12)
    elif role == "dad": # 안경
        pygame.draw.rect(surface, (71, 85, 105), (x - 35, y - 38, 70, 25), border_radius=10)
        pygame.draw.circle(surface, (51, 65, 85), (x - 12, y - 5), 10, 2)
        pygame.draw.circle(surface, (51, 65, 85), (x + 12, y - 5), 10, 2)
    else: # 기본 친구/나
        pygame.draw.arc(surface, (30, 41, 59), (x - 35, y - 40, 70, 45), 0, 3.14, 14)

    # 볼터치
    pygame.draw.circle(surface, (251, 113, 133), (x - 18, y + 8), 6)
    pygame.draw.circle(surface, (251, 113, 133), (x + 18, y + 8), 6)

    # 눈
    if expression == "sad":
        pygame.draw.line(surface, TEXT_DARK, (x - 18, y - 5), (x - 10, y - 2), 3)
        pygame.draw.line(surface, TEXT_DARK, (x + 10, y - 2), (x + 18, y - 5), 3)
    elif expression == "angry":
        pygame.draw.line(surface, TEXT_DARK, (x - 18, y - 8), (x - 10, y - 2), 3)
        pygame.draw.line(surface, TEXT_DARK, (x + 10, y - 2), (x + 18, y - 8), 3)
    else: # happy
        pygame.draw.circle(surface, TEXT_DARK, (x - 14, y - 5), 3)
        pygame.draw.circle(surface, TEXT_DARK, (x + 14, y - 5), 3)

    # 입
    if expression == "sad":
        pygame.draw.arc(surface, TEXT_DARK, (x - 10, y + 12, 20, 12), 0, 3.14, 2)
    elif expression == "angry":
        pygame.draw.line(surface, TEXT_DARK, (x - 10, y + 15), (x + 10, y + 15), 2)
    else:
        pygame.draw.arc(surface, TEXT_DARK, (x - 10, y + 5, 20, 12), 3.14, 6.28, 2)

def draw_speech_bubble(surface, text, x, y, w, h):
    # 말풍선 카키/흰색 카드
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, CARD_BG, rect, border_radius=15)
    pygame.draw.rect(surface, PRIMARY, rect, 2, border_radius=15)
    
    # 꼬리표
    points = [(x - 12, y + 25), (x, y + 15), (x, y + 35)]
    pygame.draw.polygon(surface, CARD_BG, points)
    pygame.draw.lines(surface, PRIMARY, False, [(x, y + 15), (x - 12, y + 25), (x, y + 35)], 2)

    # 텍스트 출력
    words = text.split('\n')
    for i, line in enumerate(words):
        txt_sf = FONT_BODY.render(line, True, TEXT_DARK)
        surface.blit(txt_sf, (x + 20, y + 15 + i * 24))

# UI 버튼 및 입력창 클래스
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.hover = False

    def draw(self, surface):
        bg = PRIMARY if self.hover else CARD_BG
        border = PRIMARY_DARK if self.hover else CARD_BORDER
        text_color = WHITE if self.hover else TEXT_DARK

        pygame.draw.rect(surface, bg, self.rect, border_radius=12)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=12)

        lines = self.text.split('\n')
        start_y = self.rect.centery - (len(lines) * 20 // 2)
        for i, line in enumerate(lines):
            txt_sf = FONT_BODY.render(line, True, text_color)
            txt_rect = txt_sf.get_rect(center=(self.rect.centerx, start_y + i * 22))
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
        surface.blit(txt_sf, (self.rect.x + 12, self.rect.y + 10))

# ================= 10개 문제 데이터베이스 =================
QUESTIONS = [
    {
        "cat": "1단계: 나-전달법 (행동 묘사)",
        "role": "sister", "exp": "angry",
        "dialogue": "동생이 허락 없이 내 물건을 사용해서 방이 어지러워진 상황!",
        "q": "비난 없이 '상대방의 행동'만 객관적으로 표현한 것은?",
        "options": [
            ("너는 왜 매번 허락도 없이 내 물건을 마음대로 쓰니?", False),
            ("내 허락 없이 방 물건을 사용하고 정리하지 않았어.", True),
            ("넌 항상 버릇없이 남의 물건에 손을 대더라.", False)
        ]
    },
    {
        "cat": "2단계: 나-전달법 (영향 및 감정)",
        "role": "friend", "exp": "sad",
        "dialogue": "친구와 약속을 했는데 30분 넘게 연락도 없이 늦은 상황!",
        "q": "나의 '영향과 솔직한 감정'을 바르게 표현한 것은?",
        "options": [
            ("오랫동안 기다리면서 걱정되고 내 시간이 허비되어 속상했어.", True),
            ("너 진짜 시간 개념 없다. 약속을 왜 하니?", False),
            ("다시는 너랑 약속 잡나 봐라. 기분 정말 망쳤어.", False)
        ]
    },
    {
        "cat": "3단계: 나-전달법 (바라는 사항)",
        "role": "dad", "exp": "sad",
        "dialogue": "부모님이 내 이야기나 의견을 듣지 않고 일방적으로 결정하셨을 때!",
        "q": "상대방에게 올바르게 '바라는 사항'을 요청하는 문장은?",
        "options": [
            ("제 의견도 먼저 들어보고 함께 결정해 주셨으면 좋겠어요.", True),
            ("부모님 마음대로 하실 거면 저한테 물어보지도 마세요!", False),
            ("앞으로는 저한테 아무것도 시키지 마세요.", False)
        ]
    },
    {
        "cat": "4단계: 너-전달법 $\\rightarrow$ 나-전달법 변환",
        "role": "sister", "exp": "angry",
        "dialogue": "비난조의 말: \"너는 왜 내가 말할 때마다 말을 끊고 딴소리야?\"",
        "q": "위 '너-전달법'을 올바른 '나-전달법'으로 바꾼 것은?",
        "options": [
            ("내가 말할 때 중간에 끊기면 존중받지 못하는 느낌이 들어.", True),
            ("너나 말 잘해. 왜 남의 말에 태클이니?", False),
            ("말 좀 끝까지 듣는 예의를 갖춰줬으면 좋겠다.", False)
        ]
    },
    {
        "cat": "5단계: 나-전달법 3요소 완성",
        "role": "friend", "exp": "happy",
        "dialogue": "\"네가 약속 시간을 지키지 않아서(행동), 내 일정이 꼬여 속상해(영향/감정).\"",
        "q": "이 뒤에 이어질 마지막 '바라는 사항'으로 가장 적절한 것은?",
        "options": [
            ("앞으로는 늦을 것 같으면 미리 연락을 해주면 좋겠어.", True),
            ("다음부터 한 번만 더 늦으면 절교야.", False),
            ("너도 똑같이 30분 기다려봐야 정신 차리지?", False)
        ]
    },
    {
        "cat": "6단계: 경청과 공감",
        "role": "friend", "exp": "sad",
        "dialogue": "가족이나 친구가 학교에서의 성적 문제나 고민을 털어놓을 때!",
        "q": "경청과 공감의 바람직한 태도는 무엇일까요?",
        "options": [
            ("비판이나 성급한 충고를 하기 전, 상대의 기분에 먼저 공감한다.", True),
            ("잘못된 점을 즉시 지적하고 내 경험을 바탕으로훈계한다.", False),
            ("별일 아니라는 듯이 대수롭지 않게 넘기며 주제를 바꾼다.", False)
        ]
    },
    {
        "cat": "7단계: 성격별 대화법 (사고형 T)",
        "role": "dad", "exp": "happy",
        "dialogue": "원칙과 논리적 사실을 중시하는 '사고형(T)' 아빠와의 대화!",
        "q": "T형 가족 구성원과 갈등을 해결할 때 좋은 대화법은?",
        "options": [
            ("객관적인 사실과 이유를 차분하고 논리적으로 설명한다.", True),
            ("감정적으로 눈물을 흘리며 내 기분만 알아달라고 떼를 쓴다.", False),
            ("상대방의 논리적 오류를 지적하며 언쟁에서 이기려 한다.", False)
        ]
    },
    {
        "cat": "8단계: 성격별 대화법 (감정형 F)",
        "role": "sister", "exp": "sad",
        "dialogue": "관계와 공감, 마음의 공유를 중시하는 '감정형(F)' 동생과의 대화!",
        "q": "F형 가족 구성원의 마음을 열 수 있는 대화법은?",
        "options": [
            ("옳고 그름을 따지기 전에 상대가 느꼈을 감정을 인정해 준다.", True),
            ("너의 감정은 비이성적이라며 차갑게 사실만 지적한다.", False),
            ("해결책만 빠르게 제시하고 대화를 신속히 끝낸다.", False)
        ]
    },
    {
        "cat": "9단계: 가족 갈등 해결 4단계",
        "role": "friend", "exp": "happy",
        "dialogue": "가족 갈등을 해결하는 체계적인 4단계 프로세스!",
        "q": "교과서에 제시된 올바른 갈등 해결 순서는?",
        "options": [
            ("갈등 확인 $\\rightarrow$ 해결 방법 탐색 $\\rightarrow$ 해결 방법 결정 $\\rightarrow$ 실행 및 평가", True),
            ("해결 방법 결정 $\\rightarrow$ 갈등 확인 $\\rightarrow$ 실행 및 평가 $\\rightarrow$ 해결 방법 탐색", False),
            ("갈등 확인 $\\rightarrow$ 실행 및 평가 $\\rightarrow$ 해결 방법 탐색 $\\rightarrow$ 해결 방법 결정", False)
        ]
    },
    {
        "cat": "10단계: 바람직한 대화 태도",
        "role": "dad", "exp": "angry",
        "dialogue": "갈등 상황에서 대화할 때 지켜야 할 기본 규칙!",
        "q": "다음 중 갈등 해결 대화 시 '피해야 할' 행동은?",
        "options": [
            ("과거의 지난 잘못이나 상대방의 인격/약점을 건드리는 발언", True),
            ("언어적 표현과 비언어적 표현(표정, 말투)을 일치시키기", False),
            ("현재 발생한 핵심 문제 자체에만 초점을 맞추어 대화하기", False)
        ]
    }
]

# Google Sheet 데이터 전송 함수 (Apps Script API 연동)
def submit_to_google_sheet(std_id, name, score):
    # Google Apps Script Web App URL (시트 연동용)
    script_url = "https://script.google.com/macros/s/AKfycbx_YOUR_SCRIPT_ID/exec" 
    
    payload = json.dumps({"std_id": std_id, "name": name, "score": score})
    
    if window: # Pygbag 브라우저 실행 시
        try:
            window.fetch(script_url, {
                'method': 'POST',
                'headers': {'Content-Type': 'application/json'},
                'body': payload,
                'mode': 'no-cors'
            })
            return True
        except Exception as e:
            print("Fetch Error:", e)
            return False
    return True

# ================= 메인 루프 =================
async def main():
    clock = pygame.time.Clock()
    
    q_idx = 0
    score = 0
    feedback_msg = ""
    feedback_color = ACCENT_GREEN

    # 제출 폼 필드
    id_input = InputBox(330, 260, 300, 40, "예: 10101")
    name_input = InputBox(330, 320, 300, 40, "예: 홍길동")
    submit_btn = Button(380, 380, 200, 45, "구글 시트에 제출")
    submitted = False

    buttons = []
    def load_question():
        nonlocal buttons
        buttons = []
        opts = QUESTIONS[q_idx]["options"]
        for idx, (text, is_correct) in enumerate(opts):
            btn = Button(80, 290 + idx * 75, 800, 62, text)
            buttons.append((btn, is_correct))

    load_question()
    running = True

    while running:
        screen.fill(BG_COLOR)
        pos = pygame.mouse.get_pos()

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if q_idx < 10:
                for btn, is_correct in buttons:
                    btn.check_hover(pos)
                    if event.type == pygame.MOUSEBUTTONDOWN and btn.rect.collidepoint(pos):
                        if is_correct:
                            score += 10
                            feedback_msg = "정답입니다! 올바른 의사소통 표현입니다. (+10점)"
                            feedback_color = ACCENT_GREEN
                        else:
                            feedback_msg = "오답입니다! 상대방을 비난하거나 부적절한 대화법입니다."
                            feedback_color = ERROR_RED
                        
                        q_idx += 1
                        if q_idx < 10:
                            load_question()
                        break
            else: # 결과 제출 페이지
                id_input.handle_event(event)
                name_input.handle_event(event)
                submit_btn.check_hover(pos)
                
                if event.type == pygame.MOUSEBUTTONDOWN and submit_btn.rect.collidepoint(pos) and not submitted:
                    if id_input.text and name_input.text:
                        submit_to_google_sheet(id_input.text, name_input.text, score)
                        submitted = True
                        feedback_msg = "성공적으로 제출되었습니다!"
                        feedback_color = ACCENT_GREEN
                    else:
                        feedback_msg = "학번과 이름을 모두 입력해 주세요!"
                        feedback_color = ERROR_RED

        # 상단 헤더
        pygame.draw.rect(screen, PRIMARY, (0, 0, WIDTH, 65))
        title_txt = FONT_TITLE.render("가족 의사소통 & 갈등 해결 마스터", True, WHITE)
        screen.blit(title_txt, (25, 18))
        
        score_txt = FONT_SUB.render(f"점수: {score}점 / 100점", True, WHITE)
        screen.blit(score_txt, (WIDTH - 180, 20))

        # 문제 화면 / 결과 화면 분기
        if q_idx < 10:
            q_data = QUESTIONS[q_idx]

            # 카테고리 & 진행도
            cat_txt = FONT_SUB.render(f"Q{q_idx+1}. [{q_data['cat']}]", True, PRIMARY_DARK)
            screen.blit(cat_txt, (40, 80))

            # 귀여운 캐릭터 삽화 및 말풍선
            draw_avatar(screen, 90, 180, role=q_data["role"], expression=q_data["exp"])
            draw_speech_bubble(screen, q_data["dialogue"], 150, 135, 750, 80)

            # 질문 텍스트
            q_txt = FONT_TITLE.render(q_data["q"], True, TEXT_DARK)
            screen.blit(q_txt, (40, 240))

            # 보기 버튼들
            for btn, _ in buttons:
                btn.draw(screen)

        else: # 최종 결과 & 제출 화면
            pygame.draw.rect(screen, WHITE, (180, 90, 600, 360), border_radius=16)
            pygame.draw.rect(screen, PRIMARY, (180, 90, 600, 360), 3, border_radius=16)

            res_title = FONT_TITLE.render("🎉 학습 완료! 결과를 제출하세요", True, PRIMARY_DARK)
            screen.blit(res_title, (WIDTH//2 - res_title.get_width()//2, 120))

            final_score_txt = FONT_SUB.render(f"최종 점수: {score}점", True, TEXT_DARK)
            screen.blit(final_score_txt, (WIDTH//2 - final_score_txt.get_width()//2, 170))

            # 입력 항목 표기
            lbl_id = FONT_BODY.render("학번:", True, TEXT_DARK)
            lbl_name = FONT_BODY.render("이름:", True, TEXT_DARK)
            screen.blit(lbl_id, (270, 268))
            screen.blit(lbl_name, (270, 328))

            id_input.draw(screen)
            name_input.draw(screen)
            
            if not submitted:
                submit_btn.draw(screen)
            else:
                done_txt = FONT_TITLE.render("✓ 제출이 완료되었습니다", True, ACCENT_GREEN)
                screen.blit(done_txt, (WIDTH//2 - done_txt.get_width()//2, 390))

        # 하단 피드백 메시지
        if feedback_msg:
            fb_txt = FONT_BODY.render(feedback_msg, True, feedback_color)
            screen.blit(fb_txt, (WIDTH//2 - fb_txt.get_width()//2, 495))

        pygame.display.flip()
        await asyncio.sleep(0) # Pygbag 호환 핵심

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
