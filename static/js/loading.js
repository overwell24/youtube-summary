function handleSubmit(event) {
    event.preventDefault(); // 기본 폼 동작 막기
    const submitButton = document.getElementById("button");
    submitButton.value = "요약 중..."; // 버튼 텍스트 변경

    setTimeout(() => {
        document.querySelector(".urlcontainer").submit(); // 폼 제출
    }, 30); // 3초 후 실행
}
