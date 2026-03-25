"""
Dataset generation module for training data creation.

This module provides classes for generating and managing training datasets
with proper OOP design principles.
"""

import json
import random
from typing import Dict, List, Any, Optional
from pathlib import Path
from app.prompt_builder import build_prompt_sllm


# JSON 파일 입출력 함수
def load_json_file(file_path: str) -> Dict[str, Any] | List[Dict[str, Any]]:
    """
    JSON 파일을 로드합니다.

    Args:
        file_path: JSON 파일 경로

    Returns:
        로드된 JSON 데이터

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 때
        json.JSONDecodeError: JSON 형식이 잘못되었을 때
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_file(
    file_path: str,
    data: Dict[str, Any] | List[Dict[str, Any]],
    indent: int = 2
) -> None:
    """
    JSON 파일로 저장합니다.

    Args:
        file_path: 저장할 파일 경로
        data: 저장할 데이터
        indent: JSON 들여쓰기 레벨
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def load_json_list(dataset_path: str) -> List[Dict[str, Any]]:
    """
    JSON 리스트 파일을 로드합니다.

    Args:
        dataset_path: JSON 파일 경로

    Returns:
        딕셔너리 리스트

    Raises:
        ValueError: JSON이 리스트 형태가 아닐 때
    """
    data = load_json_file(dataset_path)
    if not isinstance(data, list):
        raise ValueError("입력 JSON은 반드시 리스트 형태여야 합니다.")
    return data


class TemplateBuilder:
    """템플릿을 생성하고 관리하는 클래스"""

    REQUIRED_KEYS = {"name", "relationName", "chatStyleName"}
    VALID_RELATIONS = {"엄마", "아빠", "할머니", "할아버지"}

    def __init__(
        self,
        example_path: str,
        chat_style_path: str,
        template_guide_path: str
    ):
        """
        TemplateBuilder 초기화

        Args:
            example_path: 예제 JSON 파일 경로
            chat_style_path: 채팅 스타일 JSON 파일 경로
            template_guide_path: 템플릿 가이드 JSON 파일 경로
        """
        self.example_path = example_path
        self.chat_style_path = chat_style_path
        self.template_guide_path = template_guide_path

        self._example_data: Optional[Dict[str, Any]] = None
        self._chat_styles: Optional[Dict[str, str]] = None
        self._template_guide: Optional[Dict[str, Any]] = None

    @property
    def example_data(self) -> Dict[str, Any]:
        """예제 데이터를 지연 로딩합니다."""
        if self._example_data is None:
            self._example_data = load_json_file(self.example_path)
        return self._example_data

    @property
    def chat_styles(self) -> Dict[str, str]:
        """채팅 스타일 데이터를 지연 로딩합니다."""
        if self._chat_styles is None:
            self._chat_styles = load_json_file(self.chat_style_path)
        return self._chat_styles

    @property
    def template_guide(self) -> Dict[str, Any]:
        """템플릿 가이드 데이터를 지연 로딩합니다."""
        if self._template_guide is None:
            self._template_guide = load_json_file(self.template_guide_path)
        return self._template_guide

    def create_empty_template(self) -> Dict[str, Any]:
        """
        예제 데이터로부터 빈 템플릿 구조를 생성합니다.
        필수 키는 빈 문자열로, 선택적 키는 None으로 설정합니다.

        Returns:
            키와 기본값을 가진 템플릿 딕셔너리
        """
        template = {}

        for key in self.example_data.keys():
            if key in self.REQUIRED_KEYS:
                template[key] = ""
            else:
                template[key] = None

        return template

    def add_random_chat_style(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        템플릿에 랜덤 채팅 스타일을 추가합니다.

        Args:
            template: 채울 템플릿 딕셔너리

        Returns:
            chatStyleName이 채워진 템플릿
        """
        template["chatStyleName"] = random.choice(list(self.chat_styles.keys()))
        return template

    def build_template(self) -> Dict[str, Any]:
        """
        랜덤 채팅 스타일이 포함된 완전한 템플릿을 생성합니다.

        Returns:
            데이터 생성 준비가 완료된 템플릿
        """
        template = self.create_empty_template()
        template = self.add_random_chat_style(template)
        return template


class PromptGenerator:
    """데이터셋 및 훈련 데이터를 위한 프롬프트를 생성하는 클래스"""

    def __init__(self, relations: set = None):
        """
        PromptGenerator 초기화

        Args:
            relations: 유효한 관계명 집합
        """
        self.relations = relations or TemplateBuilder.VALID_RELATIONS

    def create_dataset_prompt(
        self,
        chat_style_guide: Dict[str, str],
        template_guide: Dict[str, Any]
    ) -> str:
        """
        데이터셋 생성을 위한 프롬프트를 생성합니다.

        Args:
            chat_style_guide: 채팅 스타일 정의
            template_guide: 템플릿 구조 가이드

        Returns:
            포맷된 프롬프트 문자열
        """
        return f"""
당신은 인간관계를 섬세하게 이해하는 대화 생성 AI입니다.
아래 JSON 템플릿의 빈 값을 자연스럽고 현실적으로 채워주세요.

규칙:
1. 출력은 반드시 JSON 형식만 사용하세요.
2. key 구조는 절대 변경하지 마세요.
3. chatContent는 가장 중요하며, 반드시 chatStyleName의 말투 특성을 강하게 반영해야 합니다.
4. Optional 필드(None)는 맥락상 자연스럽다면 채워도 되고, 불필요하면 null로 유지해도 됩니다.
5. chatContent는 실제 사람이 보낸 메시지처럼 자연스러워야 합니다.
6. relationName은 {self.relations} 중 하나를 선택합니다.

템플릿 설명:
{json.dumps(template_guide, ensure_ascii=False, indent=2)}


chatStyleName 설명:
{json.dumps(chat_style_guide, ensure_ascii=False, indent=2)}

채워야 할 JSON 템플릿:
""".strip()

    def create_training_prompt(
        self,
        prompt_data: List[Dict[str, Any]]
    ) -> str:
        """
        훈련 데이터 완성을 위한 프롬프트를 생성합니다.

        Args:
            prompt_data: 프롬프트-완성 쌍 리스트

        Returns:
            포맷된 훈련 프롬프트 문자열
        """
        return f"""
당신은 인간관계를 섬세하게 이해하는 대화 생성 AI입니다.
아래 훈련용 JSON 템플릿의 completion 값을 자연스럽고 현실적으로 채워주세요.

규칙:
1. 출력은 반드시 JSON 형식만 사용하세요.
2. key 구조는 절대 변경하지 마세요.
3. prompt를 기반으로 적절한 출력을 "completion" 란에 채워주세요.

채워야 할 JSON 템플릿:
{json.dumps(prompt_data, ensure_ascii=False, indent=2)}
""".strip()


class DatasetManager:
    """데이터셋 파일 작성 및 변환을 관리하는 클래스"""

    def __init__(self, template_builder: TemplateBuilder):
        """
        DatasetManager 초기화

        Args:
            template_builder: 템플릿 생성을 위한 TemplateBuilder 인스턴스
        """
        self.template_builder = template_builder

    def write_templates_to_file(
        self,
        output_path: str,
        base_prompt: str,
        repeat: int = 10
    ) -> None:
        """
        데이터셋 템플릿을 텍스트 파일로 작성합니다.

        Args:
            output_path: 출력 파일 경로
            base_prompt: 파일 시작 부분에 포함할 기본 프롬프트
            repeat: 생성할 템플릿 개수
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            # 기본 프롬프트 작성
            f.write(base_prompt)
            f.write("\n\n[\n\n")

            # 여러 템플릿 작성
            for i in range(repeat):
                template = self.template_builder.build_template()
                f.write(json.dumps(template, ensure_ascii=False, indent=2))
                f.write(",\n\n")

            f.write("]")

    def convert_to_prompt_completion_pairs(
        self,
        items: List[Dict[str, Any]],
        save_path: str
    ) -> List[Dict[str, Any]]:
        """
        아이템들을 프롬프트-완성 쌍으로 변환합니다.

        Args:
            items: 데이터 아이템 리스트
            save_path: 변환된 데이터를 저장할 경로

        Returns:
            프롬프트-완성 쌍 리스트
        """
        results = []

        for item in items:
            prompt = build_prompt_sllm(item)
            results.append({
                "prompt": prompt,
                "completion": ""
            })

        save_json_file(save_path, results)
        return results


class DatasetPipeline:
    """데이터셋 생성 워크플로우를 위한 메인 파이프라인"""

    def __init__(
        self,
        example_path: str = "./prompts/example.json",
        chat_style_path: str = "./prompts/chatStyleName.json",
        template_guide_path: str = "./prompts/template.json"
    ):
        """
        DatasetPipeline 초기화

        Args:
            example_path: 예제 JSON 경로
            chat_style_path: 채팅 스타일 JSON 경로
            template_guide_path: 템플릿 가이드 JSON 경로
        """
        self.template_builder = TemplateBuilder(
            example_path,
            chat_style_path,
            template_guide_path
        )
        self.prompt_generator = PromptGenerator()
        self.dataset_manager = DatasetManager(self.template_builder)

    def generate_dataset_file(
        self,
        output_path: str,
        repeat: int = 10
    ) -> str:
        """
        완전한 데이터셋 파일을 생성합니다.

        Args:
            output_path: 데이터셋 파일을 저장할 경로
            repeat: 생성할 템플릿 개수

        Returns:
            생성된 기본 프롬프트
        """
        # 기본 프롬프트 생성
        base_prompt = self.prompt_generator.create_dataset_prompt(
            self.template_builder.chat_styles,
            self.template_builder.template_guide
        )

        # 데이터셋 파일 작성
        self.dataset_manager.write_templates_to_file(
            output_path,
            base_prompt,
            repeat
        )

        return base_prompt

    def generate_training_file(
        self,
        dataset_path: str,
        prompt_output_path: str,
        training_prompt_path: str
    ) -> str:
        """
        데이터셋으로부터 훈련 프롬프트 파일을 생성합니다.

        Args:
            dataset_path: 데이터셋 JSON 경로
            prompt_output_path: 프롬프트-완성 쌍을 저장할 경로
            training_prompt_path: 훈련 프롬프트를 저장할 경로

        Returns:
            생성된 훈련 프롬프트
        """
        # 데이터셋 로드 및 변환
        items = load_json_list(dataset_path)
        prompt_data = self.dataset_manager.convert_to_prompt_completion_pairs(
            items,
            prompt_output_path
        )

        # 훈련 프롬프트 생성 및 저장
        training_prompt = self.prompt_generator.create_training_prompt(
            prompt_data
        )

        with open(training_prompt_path, "w", encoding="utf-8") as f:
            f.write(training_prompt)

        return training_prompt


def main():
    """테스트를 위한 메인 진입점"""
    pipeline = DatasetPipeline()

    # 데이터셋 생성
    base_prompt = pipeline.generate_dataset_file(
        output_path="dataset_template.txt",
        repeat=10
    )

    # 샘플 출력 표시
    template = pipeline.template_builder.build_template()
    print(base_prompt)
    print(json.dumps(template, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
