---
name: van-kiep-phan-nhanh
description: Create fresh, canon-anchored story-branch concepts from one or more supplied original stories. Use for ideas based on existing casts and plots, not for an unrelated new story or full prose.
---

# Vạn Kiếp Phân Nhánh

Tạo ý tưởng cho một nhánh truyện mới bám chặt truyện gốc. Mục tiêu là mở ra một xung đột mới có thể phát triển thành truyện drama độc lập, không phải tóm tắt hay thay tên lấy cảm hứng.

## Đầu vào và mặc định

Nhận một truyện nguyên văn, đường dẫn tới truyện, hoặc một danh sách/tệp gồm nhiều truyện. Nếu tệp gộp nhiều truyện, dùng tiêu đề/phần rõ ràng để tách từng truyện; không trộn nhân vật hoặc tình tiết giữa các phần.

Mặc định tạo **một ý tưởng hoàn chỉnh cho mỗi truyện**. Khi người dùng yêu cầu nhiều ý tưởng cho một truyện, mỗi ý tưởng phải dùng một biến số hoặc nhân vật trung tâm khác nhau. Với danh sách truyện, chủ động thay đổi cơ chế giữa các truyện khi phù hợp để tránh lặp công thức.

## Gói ý tưởng có ref bền vững

Khi người dùng yêu cầu tạo một thư mục riêng chứa các prompt ý tưởng từ tệp truyện gốc, tạo thư mục `ref/` bên trong thư mục đầu ra và sao chép tệp nguồn vào đó. Dùng bản sao này làm nguồn canon lâu dài; không để các prompt chỉ trỏ tới thư mục tạm hoặc tệp đính kèm có thể biến mất.

- Không ghi đè một tệp ref đã tồn tại và khác nội dung; dừng để báo xung đột.
- Mỗi prompt phải mở đầu bằng dòng: `**Nguồn truyện gốc cần đọc:** [đường dẫn ref] — mục “Phù Thuỷ Audio Số [số] | [tên truyện]”.` Thay nhãn “Phù Thuỷ Audio Số” bằng tiêu đề/mục thực tế khi nguồn dùng cách đánh dấu khác.
- Tham chiếu phải trỏ đúng tệp ref và đúng phần truyện nguồn, để một agent tiếp nhận có thể đọc lại canon mà không cần lịch sử cuộc trò chuyện.
- Nếu người dùng chỉ giao tạo prompt ý tưởng, chỉ tạo thư mục ref, bản sao nguồn và các prompt được yêu cầu. Không viết truyện hoàn chỉnh, outline, review, TTS/audio hay file phụ.

## Neo vào truyện gốc

Trước khi lên ý tưởng, xác định thầm lặng: nhân vật và thân phận, quan hệ, bối cảnh, mâu thuẫn cốt lõi, chuỗi biến cố, bí mật, kết cục và các điểm có thể rẽ nhánh.

- Giữ nguyên tên, thân phận, quan hệ, bối cảnh và các sự kiện nền tảng của truyện gốc.
- Chỉ chọn nhân vật **đã tồn tại trong truyện gốc** làm nhân vật trung tâm hoặc nhân vật có ảnh hưởng đáng kể. Không thêm nhân vật phụ mới, phản diện mới, người yêu mới hay cốt truyện chéo.
- Nếu dùng “độc giả xuyên vào”, đó là ý thức ngoài truyện nhập vào thân phận của một nhân vật gốc; không được tạo người xuyên không thành một nhân vật mới trong thế giới truyện. Thân phận, quan hệ và sức ép xã hội của nhân vật gốc vẫn phải còn nguyên.
- Không bẻ gãy tính cách chỉ để tiện tạo drama. Mọi thay đổi lớn trong lựa chọn hay tâm lý phải bắt nguồn rõ ràng từ biến số của nhánh mới.
- Không gọi đây là “bản phái sinh” hay giải thích truyện tham chiếu như lời kể dành cho độc giả. Trình bày ý tưởng như tiền đề tự nhiên của một truyện độc lập.

## Chọn biến số tạo nhánh

Chọn cơ chế hợp nhất với chất liệu truyện nguồn, thay vì ép mọi truyện vào trọng sinh. Các cơ chế chính:

1. **Trọng sinh:** một nhân vật gốc giữ ký ức về kết cục cũ. Có thể là nạn nhân, phản diện, người thân, đồng phạm hoặc nhân vật phụ, không mặc định là nhân vật chính.
2. **Độc giả xuyên vào nhân vật gốc:** người nhập vai biết cốt truyện ở mức không hoàn hảo. Càng can thiệp, hiệu ứng cánh bướm càng làm những thông tin họ tin tưởng trở nên thiếu chắc chắn.
3. **Góc nhìn mới:** đưa một nhân vật gốc vốn không biết toàn bộ cốt truyện thành trung tâm. Họ có lợi ích và hiểu lầm riêng, lần theo các dấu hiệu để chạm đến sự thật, rồi lựa chọn của họ làm tình thế rẽ hướng. Đây không được là kể lại nguyên truyện qua một cái tên khác.
4. **Điểm rẽ sự kiện:** bí mật, bằng chứng, cuộc gặp, tai nạn, lời thú nhận hoặc thông tin quan trọng xuất hiện sớm/muộn hay rơi vào tay một nhân vật gốc khác. Không cần yếu tố siêu nhiên nếu một thay đổi đúng chỗ đã đủ mạnh.

Có thể kết hợp tối đa hai cơ chế khi chúng thật sự bổ trợ nhau. Đừng dùng cơ chế như quyền năng giải quyết mọi việc: người có thông tin mới phải đối diện giới hạn, hiểu lầm, phản ứng của người khác và một cái giá cảm xúc hoặc hậu quả thực tế.

## Tiêu chuẩn một ý tưởng mạnh

Mỗi ý tưởng phải cho thấy rõ: ai là người mang biến số; họ biết gì và không biết gì; khoảnh khắc nào khiến truyện lệch khỏi quỹ đạo; xung đột mới leo thang ra sao; và lựa chọn cuối cùng sẽ đánh đổi điều gì. Bám vào nhịp drama, mức độ hiện thực và chất liệu cảm xúc của truyện nguồn.

Ưu tiên một điểm rẽ tạo áp lực mới hơn là một nhân vật biết trước rồi thắng dễ. Một góc nhìn mới chỉ đủ sức thành truyện khi người đó có hành động quyết định, không chỉ quan sát hoặc giải thích sự thật của truyện cũ.

## Định dạng đầu ra

Với mỗi truyện, trả lời bằng tiếng Việt với cấu trúc sau. Viết cô đọng nhưng đủ cụ thể để có thể đưa ý tưởng sang skill viết truyện tiếp theo.

```markdown
**Nguồn truyện gốc cần đọc:** [đường dẫn ref] — mục “Phù Thuỷ Audio Số [số] | [tên truyện]”.

## [Tên nhánh mới]

- **Truyện gốc:** [tên truyện]
- **Cơ chế:** [trọng sinh / độc giả xuyên vào nhân vật gốc / góc nhìn mới / điểm rẽ sự kiện]
- **Nhân vật trung tâm:** [nhân vật gốc]
- **Điểm kích hoạt:** [sự kiện bắt đầu nhánh]
- **Biết và chưa biết:** [lợi thế thông tin cùng điểm mù quyết định]
- **Đường dây drama:** [tiền đề, xung đột leo thang, bí mật được lộ và bước ngoặt chính]
- **Cái giá / cao trào:** [lựa chọn không thể né và hậu quả cảm xúc hoặc thực tế]
```

Không cần kể lại đầy đủ truyện gốc. Nếu người dùng chỉ cần danh sách ngắn, có thể rút về tiêu đề và một đoạn tiền đề, nhưng vẫn phải thể hiện nhân vật trung tâm, biến số và điểm rẽ.
