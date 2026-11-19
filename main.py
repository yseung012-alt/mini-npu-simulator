import time
import json

def calculate_mac(pattern, filter_matrix):
    score = 0.0

    for i in range(len(pattern)):
        for j in range(len(pattern[i])):
            score += pattern[i][j] * filter_matrix[i][j]

    return score


def input_matrix(name):
    matrix = []

    print(f"\n{name}을(를) 입력하세요.")

    for i in range(3):
        while True:
            try:
                values = list(map(float, input(f"{i + 1}행: ").split()))

                if len(values) != 3:
                    print("오류: 숫자 3개를 입력해야 합니다.")
                    continue

                matrix.append(values)
                break

            except ValueError:
                print("오류: 숫자만 입력해야 합니다.")

    return matrix


def run_user_mode():
    cross_filter = input_matrix("Cross 필터")
    x_filter = input_matrix("X 필터")
    pattern = input_matrix("입력 패턴")

    print("\n입력된 필터와 패턴을 저장했습니다.")

    # MAC 점수 계산
    cross_score = calculate_mac(pattern, cross_filter)
    x_score = calculate_mac(pattern, x_filter)

    # MAC 연산 시간 10회 반복 측정
    repeat = 10

    start = time.perf_counter()

    for _ in range(repeat):
        calculate_mac(pattern, cross_filter)
        calculate_mac(pattern, x_filter)

    end = time.perf_counter()

    average_ms = (end - start) * 1000 / repeat



    print("\nCross MAC 점수:", cross_score)
    print("X MAC 점수:", x_score)
    print(f"연산 시간(평균/10회): {average_ms:.6f} ms")

    if abs(cross_score - x_score) < 1e-9:
        result = "UNDECIDED"
    elif cross_score > x_score:
        result = "Cross"
    else:
        result = "X"

    print("최종 판정:", result)

def run_json_mode():
    print("\n=== data.json 분석 ===")

    try:
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)

    except FileNotFoundError:
        print("오류: data.json 파일을 찾을 수 없습니다.")
        return

    except json.JSONDecodeError:
        print("오류: data.json 형식이 올바르지 않습니다.")
        return

    filters = data.get("filters")
    patterns = data.get("patterns")

    if not isinstance(filters, dict) or not isinstance(patterns, dict):
        print("오류: filters 또는 patterns 구조가 올바르지 않습니다.")
        return

    print("JSON 파일 로드 성공!")
    print("필터 크기:", list(filters.keys()))
    print("패턴 개수:", len(patterns))

    print("\n=== 패턴별 MAC 분석 ===")

    total = 0
    passed = 0
    failed_cases = []

    for case_name, case_data in patterns.items():
        total += 1
        print(f"\n--- {case_name} ---")

        try:
            # 케이스 이름에서 행렬 크기 추출
            parts = case_name.split("_")
            size = int(parts[1])
            filter_key = f"size_{size}"

            # 해당 크기의 필터 가져오기
            selected_filters = filters[filter_key]
            cross_filter = selected_filters["cross"]
            x_filter = selected_filters["x"]

            # 입력 패턴과 정답 라벨 가져오기
            pattern = case_data["input"]
            expected_raw = case_data["expected"]

            # 라벨 정규화
            label_map = {
                "+": "Cross",
                "cross": "Cross",
                "x": "X"
            }

            expected = label_map.get(str(expected_raw).strip().lower())

            if expected is None:
                raise ValueError("알 수 없는 expected 라벨")

            # 행렬 크기 검증
            matrices = {
                "입력 패턴": pattern,
                "Cross 필터": cross_filter,
                "X 필터": x_filter
            }

            for matrix_name, matrix in matrices.items():
                if (
                    not isinstance(matrix, list)
                    or len(matrix) != size
                    or any(
                        not isinstance(row, list) or len(row) != size
                        for row in matrix
                    )
                ):
                    raise ValueError(f"{matrix_name} 크기 불일치")

                for row in matrix:
                    for value in row:
                        if not isinstance(value, (int, float)) or isinstance(value, bool):
                            raise ValueError(f"{matrix_name}에 숫자가 아닌 값 존재")

            # MAC 점수 계산
            cross_score = calculate_mac(pattern, cross_filter)
            x_score = calculate_mac(pattern, x_filter)

            # epsilon 기반 판정
            if abs(cross_score - x_score) < 1e-9:
                result = "UNDECIDED"
            elif cross_score > x_score:
                result = "Cross"
            else:
                result = "X"

            print("Cross 점수:", cross_score)
            print("X 점수:", x_score)

            # expected와 비교
            if result == expected:
                passed += 1
                print(f"판정: {result} | expected: {expected} | PASS")
            else:
                reason = (
                    "동점 처리 규칙"
                    if result == "UNDECIDED"
                    else "예상 라벨과 판정 불일치"
                )
                failed_cases.append((case_name, reason))
                print(f"판정: {result} | expected: {expected} | FAIL ({reason})")

        except (KeyError, ValueError, TypeError, IndexError) as error:
            failed_cases.append((case_name, str(error)))
            print(f"FAIL: 데이터 또는 스키마 오류 - {error}")

    # 전체 결과 요약
    print("\n=== 결과 요약 ===")
    print("총 테스트:", total)
    print("통과:", passed)
    print("실패:", len(failed_cases))

    if failed_cases:
        print("\n실패 케이스:")
        for case_name, reason in failed_cases:
            print(f"- {case_name}: {reason}")
           
    run_performance_analysis(filters)

def benchmark_mac(pattern, filter_matrix, repeat=10):
    start = time.perf_counter()

    for _ in range(repeat):
        calculate_mac(pattern, filter_matrix)

    end = time.perf_counter()

    average_ms = (end - start) * 1000 / repeat

    return average_ms

def run_performance_analysis(filters):
    print("\n=== 성능 분석 (평균/10회) ===")
    print(f"{'크기':<10} {'평균 시간(ms)':<18} {'연산 횟수':<10}")
    print("-" * 42)

    # 3x3 기준 행렬
    cross_3 = [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0]
    ]

    test_matrices = [(3, cross_3, cross_3)]

    # JSON에 저장된 5x5, 13x13, 25x25 필터 사용
    for size in [5, 13, 25]:
        key = f"size_{size}"

        try:
            cross_filter = filters[key]["cross"]
            test_matrices.append((size, cross_filter, cross_filter))
        except (KeyError, TypeError):
            print(f"{size}x{size}: 필터를 찾을 수 없습니다.")

    for size, pattern, filter_matrix in test_matrices:
        average_ms = benchmark_mac(pattern, filter_matrix)
        operations = size * size

        print(f"{size}x{size:<7} {average_ms:<18.6f} {operations:<10}")

def main():
    print("=== Mini NPU Simulator ===")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")

    while True:
        choice = input("선택: ")

        if choice == "1":
            run_user_mode()
            break
        elif choice == "2":
            run_json_mode()
            break
        else:
            print("오류: 1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()




