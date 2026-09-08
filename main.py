import pygame
import sys
import asyncio

# Pygame 초기화
pygame.init()

# 화면 설정 (태블릿에 적합한 16:9 비율 / 960x540)
WIDTH, HEIGHT = 960, 540
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("가족 의사소통 & 갈등 해결 마스터")

# 색상 정의
WHITE = (255, 255, 255)
BG_COLOR = (245, 247, 250)
PRIMARY = (79, 70, 229)      # 보라/파랑 계열
SECONDARY = (16, 185, 129)   # 녹색 계열
TEXT_DARK = (31, 41, 55)
CARD_BG = (255, 255, 255)
CARD_BORDER = (209, 213, 219)
SUCCESS = (34, 197, 94)
ERROR = (239, 68, 68)

# 폰트 설정 (한글 지원)
def get_font(size):
    try:
        # 같은 폴더에 NanumGothic.ttf 폰트 파일이 있으면 우선 로드
        return pygame.font.Font("Gumi Romance.ttf", size)
    except:
        # 시스템 기본 한글 폰트 래핑
        return pygame.font.SysFont("malgungothic", size)

FONT_TITLE = get_font(28)
FONT_BODY = get_font(18)
FONT_CARD = get_font(16)

class Button:
    def __init__(self, x, y, width, height, text, bg_color=CARD_BG, border_color=CARD_BORDER):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.bg_color = bg_color
        self.border_color = border_color
        self.selected = False

    def draw(self, surface):
        color = PRIMARY if self.selected else self.bg_color
        border = PRIMARY if self.selected else self.border_color
        text_color = WHITE if self.selected else TEXT_DARK

        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=10)

        # 텍스트 줄바꿈 처리
        words = self.text.split('\n')
        total_h = len(words) * 22
        start_y = self.rect.centery - (total_h // 2) + 2

        for i, word in enumerate(words):
            txt_sf = FONT_CARD.render(word, True, text_color)
            txt_rect = txt_sf.get_rect(center=(self.rect.centerx, start_y + i * 22))
            surface.blit(txt_sf, txt_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

async def main():
    clock = pygame.time.Clock()
    
    # 게임 상태 관리
    stage = 1
    score = 0
    feedback_msg = ""
    feedback_color = SUCCESS

    # ================= Stage 1 : '나' 전달법 3단계 =================
    # 교과서 35쪽: 행동 묘사 -> 영향 및 감정 -> 바라는 사항
    st1_step = 1 # 1: 행동, 2: 영향/감정, 3: 바라는점
    st1_choices = {
        1: [("동생이 내 방을 정리하지 않고 어지럽혔을 때", True), ("너는 왜 항상 방을 안 치우니?", False), ("매번 비꼬며 말할 때", False)],
        2: [("내가 청소를 다시 해야 해서 속상하고 힘들어.", True), ("너 때문에 기분이 망쳤어.", False), ("앞으로 너랑은 아무것도 안 할 거야.", False)],
        3: [("사용한 물건은 제자리에 치워주면 좋겠어.", True), ("당장 방 청소부터 해!", False), ("다시는 내 방에 들어오지 마.", False)]
    }
    st1_buttons = []

    def load_st1_buttons():
        nonlocal st1_buttons
        st1_buttons = []
        options = st1_choices[st1_step]
        for idx, (text, is_correct) in enumerate(options):
            st1_buttons.append((Button(100, 200 + idx * 90, 760, 70, text), is_correct))

    load_st1_buttons()

    # ================= Stage 2 : 성격 유형별 대화 & 경청·공감 =================
    # 교과서 34~35쪽: 경청/공감/긍정적 듣기 + T/F 성격 유형
    st2_q_idx = 0
    st2_questions = [
        {
            "title": "[성격별 대화] 원칙과 사실을 중시하는 '사고형(T)' 아빠와의 바람직한 대화법은?",
            "options": [
                ("객관적인 사실을 바탕으로 차분하게 상황을 설명한다.", True),
                ("감정적으로 떼를 쓰며 내 기분만 알아달라고 요구한다.", False),
                ("상대방의 약점을 건드리며 이성적으로 따진다.", False)
            ]
        },
        {
            "title": "[경청과 공감] 고민을 털어놓는 친구/가족에게 바람직한 태도는?",
            "options": [
                ("비판이나 성급한 충고를 하기 전에 감정부터 공감하며 듣는다.", True),
                ("이야기가 끝나기도 전에 건성으로 고개만 끄덕인다.", False),
                ("잘못된 점을 즉시 지적하고 내 의견만 말한다.", False)
            ]
        }
    ]
    st2_buttons = []

    def load_st2_buttons():
        nonlocal st2_buttons
        st2_buttons = []
        q = st2_questions[st2_q_idx]
        for idx, (text, is_correct) in enumerate(q["options"]):
            st2_buttons.append((Button(100, 200 + idx * 90, 760, 70, text), is_correct))

    # ================= Stage 3 : 가족 갈등 해결 4단계 =================
    # 교과서 36쪽: 1단계 갈등확인 -> 2단계 해결방법 탐색 -> 3단계 해결방법 결정 -> 4단계 실행 및 평가
    st3_sequence = []
    st3_steps = ["1단계: 갈등 확인", "2단계: 해결 방법 탐색", "3단계: 해결 방법 결정", "4단계: 실행 및 평가"]
    st3_options = ["3단계: 해결 방법 결정", "1단계: 갈등 확인", "4단계: 실행 및 평가", "2단계: 해결 방법 탐색"]
    st3_buttons = [Button(120 + (i % 2) * 370, 220 + (i // 2) * 110, 340, 80, text) for i, text in enumerate(st3_options)]

    running = True

    while running:
        screen.fill(BG_COLOR)
        pos = pygame.mouse.get_pos()

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if stage == 1:
                    for btn, is_correct in st1_buttons:
                        if btn.is_clicked(pos):
                            if is_correct:
                                score += 20
                                feedback_msg = "올바른 '나-전달법' 선택입니다!"
                                feedback_color = SUCCESS
                                st1_step += 1
                                if st1_step > 3:
                                    stage = 2
                                    load_st2_buttons()
                                else:
                                    load_st1_buttons()
                            else:
                                feedback_msg = "상대방을 비난하거나 '너-전달법'이 포함되었습니다. 다시 고르세요!"
                                feedback_color = ERROR

                elif stage == 2:
                    for btn, is_correct in st2_buttons:
                        if btn.is_clicked(pos):
                            if is_correct:
                                score += 20
                                feedback_msg = "정답입니다! 공감과 성격 고려 대화를 실천했습니다."
                                feedback_color = SUCCESS
                                st2_q_idx += 1
                                if st2_q_idx >= len(st2_questions):
                                    stage = 3
                                else:
                                    load_st2_buttons()
                            else:
                                feedback_msg = "바람직하지 않은 대화 방식입니다. 다시 선택하세요!"
                                feedback_color = ERROR

                elif stage == 3:
                    for btn in st3_buttons:
                        if btn.is_clicked(pos) and btn.text not in st3_sequence:
                            st3_sequence.append(btn.text)
                            btn.selected = True

                            if len(st3_sequence) == 4:
                                if st3_sequence == st3_steps:
                                    score += 20
                                    stage = 4 # 완주
                                else:
                                    feedback_msg = "갈등 해결 순서가 올바르지 않습니다. 다시 시도하세요!"
                                    feedback_color = ERROR
                                    st3_sequence = []
                                    for b in st3_buttons: b.selected = False

        # ================= UI 렌더링 =================
        # 상단 헤더
        pygame.draw.rect(screen, PRIMARY, (0, 0, WIDTH, 70))
        title_txt = FONT_TITLE.render("가족 의사소통 & 갈등 해결 게임", True, WHITE)
        screen.blit(title_txt, (30, 20))
        
        score_txt = FONT_BODY.render(f"점수: {score}점", True, WHITE)
        screen.blit(score_txt, (WIDTH - 130, 25))

        # 스테이지별 내용 그리기
        if stage == 1:
            step_names = {1: "1단계: 행동 묘사 (비난 없이)", 2: "2단계: 영향 및 나의 감정", 3: "3단계: 바라는 사항 말하기"}
            q_txt = FONT_TITLE.render(f"[Stage 1] '나' 전달법 - {step_names[st1_step]}", True, TEXT_DARK)
            screen.blit(q_txt, (50, 100))
            sub_txt = FONT_BODY.render("상황: 동생이 방을 정리하지 않아 갈등이 생긴 상황입니다.", True, TEXT_DARK)
            screen.blit(sub_txt, (50, 145))

            for btn, _ in st1_buttons:
                btn.draw(screen)

        elif stage == 2:
            q_txt = FONT_TITLE.render("[Stage 2] 바람직한 의사소통 & 성격 맞춤 대화", True, TEXT_DARK)
            screen.blit(q_txt, (50, 100))
            
            q_title = st2_questions[st2_q_idx]["title"]
            sub_txt = FONT_BODY.render(q_title, True, TEXT_DARK)
            screen.blit(sub_txt, (50, 145))

            for btn, _ in st2_buttons:
                btn.draw(screen)

        elif stage == 3:
            q_txt = FONT_TITLE.render("[Stage 3] 가족 갈등 해결 4단계 순서 맞추기", True, TEXT_DARK)
            screen.blit(q_txt, (50, 100))
            sub_txt = FONT_BODY.render("올바른 갈등 해결 단계 순서대로 4개의 카드를 터치하세요.", True, TEXT_DARK)
            screen.blit(sub_txt, (50, 145))

            for btn in st3_buttons:
                btn.draw(screen)

            # 선택한 순서 표시
            seq_str = "선택 순서: " + " -> ".join([s.split(":")[0] for s in st3_sequence])
            seq_txt = FONT_BODY.render(seq_str, True, PRIMARY)
            screen.blit(seq_txt, (50, 460))

        elif stage == 4:
            pygame.draw.rect(screen, CARD_BG, (150, 120, 660, 340), border_radius=15)
            pygame.draw.rect(screen, PRIMARY, (150, 120, 660, 340), 3, border_radius=15)

            end_title = FONT_TITLE.render("🎉 대화 & 갈등 해결 마스터 달성!", True, PRIMARY)
            screen.blit(end_title, (WIDTH//2 - end_title.get_width()//2, 160))

            summary_lines = [
                f"최종 점수: {score}점 / 100점",
                "✓ '나' 전달법 3요소(행동-영향/감정-바라는점) 완수",
                "✓ 성격 차이 인정 및 경청·공감 태도 습득",
                "✓ 가족 갈등 해결 4단계 체계적 이해 완료"
            ]

            for idx, line in enumerate(summary_lines):
                txt = FONT_BODY.render(line, True, TEXT_DARK)
                screen.blit(txt, (200, 230 + idx * 40))

        # 하단 피드백 메시지 출력
        if feedback_msg and stage < 4:
            fb_txt = FONT_BODY.render(feedback_msg, True, feedback_color)
            screen.blit(fb_txt, (WIDTH//2 - fb_txt.get_width()//2, 495))

        pygame.display.flip()
        await asyncio.sleep(0)  # Pygbag 호환을 위한 핵심 구문!

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
