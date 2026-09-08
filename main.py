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

# 색상 파렛트
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

# 폰트 로드 (font.ttf 파일 필요)
def get_font(size, bold=False):
    try:
        return pygame.font.Font("font.ttf", size)
    except Exception as e:
        return pygame.font.Font(None, size)

FONT_TITLE = get_font(22, bold=True)
FONT_SUB = get_font(17, bold=True)
FONT_BODY = get_font(14)

# 캐릭터 삽화 함수
def draw_avatar(surface, x, y, role="friend", expression="happy"):
    face_color = (254, 226, 226) if role == "sister" else ((253, 230, 138) if role == "dad" else (254, 243, 199))
    pygame.draw.circle(surface, face_color, (x, y), 32)
    pygame.draw.circle(surface, (217, 119, 6), (x, y), 32, 2)

    if role == "sister":
        pygame.draw.circle(surface, (180, 83, 9), (x - 22, y - 8), 10)
        pygame.draw.circle(surface, (180, 83, 9), (x + 22, y - 8), 10)
        pygame.draw.arc(surface, (180, 83, 9), (x - 32, y - 35, 64, 45), 0, 3.14, 10)
    elif role == "dad":
        pygame.draw.rect(surface, (71, 85, 105), (x - 30, y - 32, 60, 22), border_radius=8)
        pygame.draw.circle(surface, (51, 65, 85), (x - 10, y - 5), 8, 2)
        pygame.draw.circle(surface, (51, 65, 85), (x + 10, y - 5), 8, 2)
    else:
        pygame.draw.arc(surface, (30, 41, 59), (x - 32, y - 35, 64, 40), 0, 3.14, 12)

    pygame.draw.circle(surface, (251, 113, 133), (x - 16, y + 6), 5)
    pygame.draw.circle(surface, (251, 113, 133), (x + 16, y + 6), 5)

    if expression == "sad":
        pygame.draw.line(surface, TEXT_DARK, (x - 16, y - 5), (x - 8, y - 2), 2)
        pygame.draw.line(surface, TEXT_DARK, (x + 8, y - 2), (x + 16, y - 5), 2)
        pygame.draw.arc(surface, TEXT_DARK, (x - 8, y + 10, 16, 10), 0, 3.14, 2)
    elif expression == "angry":
        pygame.draw.line(surface, TEXT_DARK, (x - 16, y - 8), (x - 8, y - 2), 2)
        pygame.draw.line(surface, TEXT_DARK, (x + 8, y - 2), (x + 16, y - 8), 2)
        pygame.draw.line(surface, TEXT_DARK, (x - 8, y + 12), (x + 8, y + 12), 2)
    else:
        pygame.draw.circle(surface, TEXT_DARK, (x - 12, y - 5), 3)
        pygame.draw.circle(surface, TEXT_DARK, (x + 12, y - 5), 3)
        pygame.draw.arc(surface, TEXT_DARK, (x - 8, y + 4, 16, 10), 3.14, 6.28, 2)

# 말풍선 함수
def draw_speech_bubble(surface, text, x, y, w, h):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, CARD_BG, rect, border_radius=12)
    pygame.draw.rect(surface, PRIMARY, rect, 2, border_radius=12)
    
    points = [(x - 10, y + 20), (x, y + 12), (x, y + 28)]
    pygame.draw.polygon(surface, CARD_BG, points)
    pygame.draw.lines(surface, PRIMARY, False, [(x, y + 12), (x - 10, y + 20), (x, y + 28)], 2)

    words = text.split('\n')
    for i, line in enumerate(words):
        txt_sf = FONT_BODY.render(line, True, TEXT_DARK)
        surface.blit(txt_sf, (x + 15, y + 10 + i * 20))

# 5지선다 맞춤형 버튼 클래스
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.hover = False

    def draw(self, surface):
        bg = PRIMARY if self.hover else CARD_BG
        border = PRIMARY_DARK if self.hover else CARD_BORDER
        text_color = WHITE if self.hover else TEXT_DARK

        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=8)

        txt_sf = FONT_BODY.render(self.text, True, text_color)
        txt_rect = txt_sf.get_rect(center=self.rect.center)
        surface.blit(txt_sf, txt_rect)

    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

# 입력창 클래스
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

# ================= 5지선다 검토 완료 질문 데이터베이스 =================
QUESTIONS = [
    {
        "cat": "1단계: 나-전달법 (행동 묘사)",
        "role": "sister", "exp": "angry",
        "dialogue": "동생이 허락 없이 학용품을 가져가 잃어버린 상황!",
        "q": "비난이나 평가 없이 상대방의 '행동'만 객관적으로 표현한 것은?",
        "options": [
            ("1. 너는 왜 매번 허락도 없이 남의 물건을 마음대로 건드리니?", False),
            ("2. 내 허락 없이 필통에서 학용품을 가져가서 잃어버렸어.", True),
            ("3. 넌 항상 정리정돈도 안 하고 무책임한 태도를 보이더라.", False),
            ("4. 남의 물건을 몰래 가져가는 건 정말 나쁜 범죄 행동이야.", False),
            ("5. 네가 자꾸 내 물건을 건드리니까 내가 항상 화가 나는 거야.", False)
        ]
    },
    {
        "cat": "2단계: 나-전달법 (영향 및 감정)",
        "role": "friend", "exp": "sad",
        "dialogue": "친구가 약속 시간에 30분 넘게 연락도 없이 늦게 온 상황!",
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
        "cat": "3단계: 나-전달법 (바라는 사항)",
        "role": "dad", "exp": "sad",
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
        "cat": "4단계: 너-전달법 → 나-전달법 변환",
        "role": "sister", "exp": "angry",
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
        "cat": "5단계: 나-전달법 3요소 완성",
        "role": "friend", "exp": "happy",
        "dialogue": "\"네가 연락 없이 약속에 늦어서(행동), 기다리며 걱정되고 속상했어(영향/감정).\"",
        "q": "이 문장 뒤에 이어질 마지막 '바라는 사항'으로 가장 적절한 것은?",
        "options": [
            ("1. 앞으로는 늦을 것 같으면 미리 나에게 연락을 해주면 좋겠어.", True),
            ("2. 다음부터 한 번만 더 늦으면 너랑 바로 절교하는 줄 알아.", False),
            ("3. 너도 똑같이 30분 동안 길거리에서 기다려 봐야 정신 차리지?", False),
            ("4. 앞으로 너와의 모든 약속은 내가 전부 취소하도록 할게.", False),
            ("5. 늦은 시간만큼 네가 맛있는 걸 사서 정식으로 사과하면 좋겠어.", False)
        ]
    },
    {
        "cat": "6단계: 경청과 공감",
        "role": "friend", "exp": "sad",
        "dialogue": "친구나 가족이 시험 성적이 떨어져 우울하다고 고민을 털어놓을 때!",
        "q": "경청과 공감의 바람직한 대화 태도는 무엇일까요?",
        "options": [
            ("1. 상대방의 평소 공부 습관과 잘못된 점을 즉시 지적해 준다.", False),
            ("2. 말하는 중간에 개입하여 나의 더 안 좋았던 경험담을 이야기한다.", False),
            ("3. 비판이나 성급한 조언 전에 상대방이 느꼈을 좌절감에 먼저 공감해 준다.", True),
            ("4. 별일 아니라는 듯 대수롭지 않게 넘기며 빠르게 주제를 바꾼다.", False),
            ("5. 해결책을 제시하기 위해 상대방의 말을 끊고 논리적으로 질문한다.", False)
        ]
    },
    {
        "cat": "7단계: 나-전달법과 비언어적 표현",
        "role": "sister", "exp": "angry",
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
        "cat": "8단계: 성격 유형별 대화 (사고형 T)",
        "role": "dad", "exp": "happy",
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
        "cat": "9단계: 성격 유형별 대화 (감정형 F)",
        "role": "sister", "exp": "sad",
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
        "cat": "10단계: 가족 갈등 해결 4단계",
        "role": "friend", "exp": "happy",
        "dialogue": "교과서에 제시된 가족 갈등 해결의 체계적인 4단계 프로세스!",
        "q": "갈등을 올바르게 해결하는 순서로 가장 적절한 것은?",
        "options": [
            ("1. 갈등 확인 → 해결 방법 탐색 → 해결 방법 결정 → 실행 및 평가", True),
            ("2. 해결 방법 결정 → 갈등 확인 → 실행 및 평가 → 해결 방법 탐색", False),
            ("3. 갈등 확인 → 실행 및 평가 → 해결 방법 탐색 → 해결 방법 결정", False),
            ("4. 해결 방법 탐색 → 갈등 확인 → 해결 방법 결정 → 실행 및 평가", False),
            ("5. 갈등 확인 → 해결 방법 결정 → 해결 방법 탐색 → 실행 및 평가", False)
        ]
    }
]

# Google Sheet 데이터 전송 함수
def submit_to_google_sheet(std_id, name, score):
    script_url = "https://script.google.com/macros/s/AKfycbxl5cVTV1iVWKtqH64oyKxFZfCK0PzBeaFWskMUk0iWaTmuiH0Ul07tKC-ms5O0Y-6f/exec" 
    payload = json.dumps({"std_id": std_id, "name": name, "score": score})
    
    if window:
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

    id_input = InputBox(330, 260, 300, 36, "예: 10101")
    name_input = InputBox(330, 315, 300, 36, "예: 홍길동")
    submit_btn = Button(380, 375, 200, 40, "구글 시트에 제출")
    submitted = False

    buttons = []
    def load_question():
        nonlocal buttons
        buttons = []
        opts = QUESTIONS[q_idx]["options"]
        # 5지선다 버튼 Y축 간격 재배치 (248px부터 시작, 높이 38px, 간격 47px)
        for idx, (text, is_correct) in enumerate(opts):
            btn = Button(80, 248 + idx * 47, 800, 38, text)
            buttons.append((btn, is_correct))

    load_question()
    running = True

    while running:
        screen.fill(BG_COLOR)
        pos = pygame.mouse.get_pos()

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
            else:
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
        pygame.draw.rect(screen, PRIMARY, (0, 0, WIDTH, 60))
        title_txt = FONT_TITLE.render("가족 의사소통 & 갈등 해결 마스터", True, WHITE)
        screen.blit(title_txt, (20, 16))
        
        score_txt = FONT_SUB.render(f"점수: {score}점 / 100점", True, WHITE)
        screen.blit(score_txt, (WIDTH - 170, 18))

        if q_idx < 10:
            q_data = QUESTIONS[q_idx]

            # 카테고리
            cat_txt = FONT_SUB.render(f"Q{q_idx+1}. [{q_data['cat']}]", True, PRIMARY_DARK)
            screen.blit(cat_txt, (40, 72))

            # 캐릭터 & 말풍선
            draw_avatar(screen, 85, 152, role=q_data["role"], expression=q_data["exp"])
            draw_speech_bubble(screen, q_data["dialogue"], 140, 115, 780, 70)

            # 질문 텍스트
            q_txt = FONT_SUB.render(q_data["q"], True, TEXT_DARK)
            screen.blit(q_txt, (40, 212))

            # 5개 보기 버튼 출력
            for btn, _ in buttons:
                btn.draw(screen)

        else: # 결과 제출 페이지
            pygame.draw.rect(screen, WHITE, (180, 85, 600, 360), border_radius=16)
            pygame.draw.rect(screen, PRIMARY, (180, 85, 600, 360), 3, border_radius=16)

            res_title = FONT_TITLE.render("학습 완료! 결과를 제출하세요", True, PRIMARY_DARK)
            screen.blit(res_title, (WIDTH//2 - res_title.get_width()//2, 115))

            final_score_txt = FONT_SUB.render(f"최종 점수: {score}점", True, TEXT_DARK)
            screen.blit(final_score_txt, (WIDTH//2 - final_score_txt.get_width()//2, 160))

            lbl_id = FONT_BODY.render("학번:", True, TEXT_DARK)
            lbl_name = FONT_BODY.render("이름:", True, TEXT_DARK)
            screen.blit(lbl_id, (270, 268))
            screen.blit(lbl_name, (270, 323))

            id_input.draw(screen)
            name_input.draw(screen)
            
            if not submitted:
                submit_btn.draw(screen)
            else:
                done_txt = FONT_TITLE.render("✓ 제출이 완료되었습니다", True, ACCENT_GREEN)
                screen.blit(done_txt, (WIDTH//2 - done_txt.get_width()//2, 385))

        # 하단 피드백 메시지
        if feedback_msg:
            fb_txt = FONT_BODY.render(feedback_msg, True, feedback_color)
            screen.blit(fb_txt, (WIDTH//2 - fb_txt.get_width()//2, 498))

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
