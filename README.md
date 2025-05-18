1. Mục tiêu
Bài toán 8-Puzzle là một trong những bài toán cổ điển trong lĩnh vực Trí tuệ nhân tạo, thường được dùng để khảo sát và đánh giá các thuật toán tìm kiếm.
Mục tiêu của đồ án là:
-	Xây dựng một hệ thống có giao diện trực quan, cho phép người dùng nhập trạng thái đầu và sử dụng nhiều thuật toán khác nhau để giải bài toán 8-Puzzle.
-	Cài đặt và so sánh các nhóm thuật toán từ không có thông tin (uninformed), có thông tin (informed), tìm kiếm cục bộ (local search), đến các thuật toán phức tạp hơn như Conformant Search, Constraint Satisfaction, và Reinforcement Learning.
-	Tạo ra minh họa trực quan bằng ảnh động (GIF) để dễ dàng theo dõi quá trình hoạt động của từng thuật toán.
Qua đó có cái nhìn toàn diện hơn về cách các thuật toán AI hoạt động trong thực tiễn và hiểu sâu hơn về ưu – nhược điểm của từng hướng tiếp cận.
2. Nội dung:
2.1. Tổng quan về bài toán tìm kiếm và giải pháp
Bài toán 8-Puzzle là một trò chơi giải đố trên một bảng 3x3 với 8 ô được đánh số từ 1 đến 8 và một ô trống (ký hiệu là 0). Mục tiêu là di chuyển các ô sao cho đạt được trạng thái đích – thường là dãy số theo thứ tự từ trái sang phải, từ trên xuống dưới, với ô trống ở góc dưới bên phải:
    1 2 3
    4 5 6
    7 8 0
Đặc điểm của bài toán:
  •	Có không gian trạng thái lớn: có 9! = 362,880 cấu hình khác nhau, trong đó chỉ khoảng một nửa là giải được
  •	Là bài toán tổ hợp: chỉ cần thay đổi vị trí là trạng thái hoàn toàn khác nhau.
  •	Chi phí các bước bằng nhau: mỗi thao tác di chuyển (lên/xuống/trái/phải) có chi phí bằng nhau.
  •	Có thể giải bằng nhiều chiến lược tìm kiếm: từ đơn giản (BFS/DFS) đến phức tạp (A*, học tăng cường,…).
Các loại thuật toán áp dụng:
  •	Tìm kiếm không có thông tin (Uninformed Search): không sử dụng tri thức bổ sung về bài toán. Ví dụ: BFS, DFS, UCS, IDDFS.
  •	Tìm kiếm có thông tin (Informed Search): sử dụng hàm heuristic để định hướng tìm kiếm. Ví dụ: A*, Greedy, IDA*.
  •	Tìm kiếm cục bộ (Local Search): không mở rộng toàn bộ không gian trạng thái, tập trung cải thiện lời giải hiện tại. Ví dụ: Hill Climbing, Simulated Annealing.
  •	Tìm kiếm trong môi trường không xác định hoặc có ràng buộc: như Conformant BFS (Belief State), CSP (Backtracking, Forward Checking), học tăng cường (Q-Learning).
Việc chọn thuật toán phụ thuộc vào:
  •	Mức độ phức tạp của bài toán
  •	Khả năng tính toán
  •	Yêu cầu về thời gian, tối ưu hoặc tính đầy đủ
Thông qua việc triển khai và đánh giá các thuật toán này, có thể hiểu rõ hơn về cách chúng hoạt động và phù hợp với loại bài toán nào.
2.2. Các thuật toán tìm kiếm không có thông tin
2.2.1. Các thuật toán triển khai trong nhóm
 	Nhóm thuật toán tìm kiếm không có thông tin (uninformed search) là những phương pháp không sử dụng thêm gì về trạng thái đích ngoài thông tin có sẵn từ không gian trạng thái. Trong đồ án này, các thuật toán sau đã được triển khai gồm:
● Breadth-First Search (BFS)
•	Duyệt theo từng lớp, mở rộng các trạng thái gần gốc trước.
•	Luôn tìm ra lời giải tối ưu nếu tồn tại.
•	Sử dụng hàng đợi (FIFO) để quản lý frontier.
● Depth-First Search (DFS)
•	Duyệt theo chiều sâu, ưu tiên đi sâu đến trạng thái cuối cùng trước khi quay lại.
•	Tốc độ nhanh, nhưng không đảm bảo tìm ra lời giải tối ưu.
•	Có thể bị kẹt ở nhánh vô hạn nếu không giới hạn độ sâu.
● Uniform Cost Search (UCS)
•	Tương tự BFS nhưng xét theo chi phí đường đi từ gốc đến trạng thái hiện tại.
•	Ưu tiên mở rộng các trạng thái có chi phí nhỏ nhất.
•	Đảm bảo tìm ra lời giải tối ưu nếu chi phí di chuyển luôn dương.
● Iterative Deepening Depth-First Search (IDDFS)
•	Kết hợp ưu điểm của DFS và BFS.
•	Chạy DFS nhiều lần với độ sâu tăng dần cho đến khi tìm thấy lời giải.
•	Đảm bảo tìm thấy lời giải tối ưu nhưng tốn thời gian do lặp lại.
2.2.2. Hình ảnh GIF minh họa hành động
Các hình ảnh dưới đây minh họa quá trình hoạt động của các thuật toán không có thông tin khi giải 8-Puzzle từ một trạng thái ban đầu về trạng thái đích:
-BFS:

![BFS](https://github.com/user-attachments/assets/e2c07a10-543a-4476-88db-6dee63249e2f)
- DFS
  
  ![DFS](https://github.com/user-attachments/assets/4a68c094-9582-49e4-b84f-bd8615be8338)
- UCS
  
 ![UCS](https://github.com/user-attachments/assets/9393d4be-0d81-4344-908c-90f495908b7c)
- IDDFS
  
![IDDFS](https://github.com/user-attachments/assets/dc8ef2a3-7739-4aa1-a311-d33f8515106b)
2.2.3. Một vài nhận xét về hiệu suất
![image](https://github.com/user-attachments/assets/98fa7b22-103e-40b9-b1fd-312004e2e0aa)
•	BFS thích hợp khi cần lời giải ngắn nhất nhưng tốn bộ nhớ lớn.
•	DFS nhanh nhưng dễ bị kẹt nếu không giới hạn độ sâu.
•	UCS phù hợp khi các bước có chi phí khác nhau (mặc dù trong 8-puzzle thường bằng nhau).
•	IDDFS là lựa chọn cân bằng, tuy nhiên hiệu năng không cao nếu độ sâu lớn.
2.3. Các thuật toán tìm kiếm có thông tin
2.3.1. Cách tiếp cận bài toán và vai trò của Heuristic
Các thuật toán tìm kiếm có thông tin (Informed Search) sử dụng heuristic – hàm đánh giá – để ước lượng khoảng cách từ trạng thái hiện tại đến trạng thái đích. Điều này giúp hạn chế không gian tìm kiếm, tăng tốc độ giải quyết bài toán so với các thuật toán không có thông tin.
Trong bài toán 8-Puzzle, hai hàm heuristic phổ biến đã được áp dụng là:
•	Manhattan Distance: Tổng khoảng cách theo chiều ngang và dọc từ vị trí hiện tại của từng ô đến vị trí đích.
•	Tiles Out of Place: Đếm số ô đang nằm sai vị trí.
Nếu Heuristic càng tốt thì thuật toán càng định hướng chính xác, giảm số bước tìm kiếm.
2.3.2. Các thuật toán triển khai trong nhóm
● Greedy Best-First Search
•	Luôn chọn trạng thái có giá trị heuristic thấp nhất.
•	Không đảm bảo lời giải tối ưu.
•	Có thể đi lạc nếu heuristic không tốt.
● A* Search
•	Kết hợp chi phí từ gốc đến hiện tại (g(n)) và heuristic (h(n)):
f(n) = g(n) + h(n)
•	Đảm bảo tìm lời giải tối ưu nếu heuristic là admissible (không đánh giá quá thấp).
•	Thường cho kết quả tốt và hiệu quả hơn BFS/UCS.
● Iterative Deepening A* (IDA*)
•	Áp dụng phương pháp lặp với ngưỡng dựa trên f(n).
•	Giảm chi phí bộ nhớ so với A*, tuy nhiên có thể chậm hơn.
2.3.3. Hình ảnh GIF minh họa hoạt động
Minh họa dưới đây thể hiện cách các thuật toán Greedy, A*, IDA* tiếp cận và giải quyết bài toán dựa trên heuristic:
-Greedy
![GREEDY](https://github.com/user-attachments/assets/f8778117-78bb-4c91-bde3-e59e68e57af3)
-A*
![A_star](https://github.com/user-attachments/assets/04f8da2b-bfc9-43ad-8bd7-fecd90c55001)
-IDA*
![IDA_star](https://github.com/user-attachments/assets/5c4e0f56-5f71-4c25-b59d-f15fe1811185)
2.3.4 Một vài nhận xét về hiệu suất
  ![image](https://github.com/user-attachments/assets/9cdff3c7-2df5-4562-833c-d3a72f996eee)
•	Greedy phù hợp khi cần giải nhanh nhưng không yêu cầu tối ưu.
•	A* là lựa chọn phổ biến nhất cho 8-Puzzle nếu bộ nhớ không bị giới hạn.
•	IDA* là phiên bản tiết kiệm bộ nhớ của A*, tuy nhiên chậm hơn do phải lặp lại.
2.4. Các thuật toán Tìm kiếm cục bộ (Local Search)
2.4.1. Cách tiếp cận bài toán
Tìm kiếm cục bộ (Local Search) là phương pháp không cố gắng xây dựng toàn bộ đường đi từ trạng thái ban đầu đến trạng thái đích. Thay vào đó, nó tìm cách cải thiện lời giải hiện tại thông qua các bước nhỏ và chỉ giữ một số lượng rất hạn chế các trạng thái trong bộ nhớ.
Đây là phương pháp rất phù hợp với không gian trạng thái lớn hoặc bài toán tối ưu hóa, nơi chi phí lưu trữ và duyệt toàn bộ cây tìm kiếm là không khả thi.
Trong bài toán 8-Puzzle, các thuật toán tìm kiếm cục bộ giúp thử nghiệm khả năng giải mà không cần duyệt toàn bộ không gian trạng thái, tuy nhiên không đảm bảo tìm được lời giải tối ưu.
2.4.2. Các thuật toán triển khai trong nhóm
● Hill Climbing (Simple, Steepest Ascent, Stochastic)
•	Simple: chọn trạng thái kề tốt hơn đầu tiên.
•	Steepest Ascent: chọn trạng thái kề có heuristic tốt nhất.
•	Stochastic: chọn ngẫu nhiên trong các trạng thái tốt hơn hiện tại.
•	Ưu điểm: đơn giản, ít tốn bộ nhớ.
•	Nhược điểm: dễ mắc kẹt tại cực trị địa phương (local minima), plateau.
● Simulated Annealing
•	Cho phép "leo xuống" (nhận lời giải xấu hơn tạm thời) với xác suất giảm dần theo thời gian.
•	Dựa trên mô hình vật lý làm nguội kim loại.
•	Giúp thoát khỏi local minima hiệu quả hơn Hill Climbing.
● Beam Search
•	Duyệt song song nhiều trạng thái nhưng giới hạn theo số lượng (beam width).
•	Giữ lại các trạng thái tốt nhất ở mỗi cấp độ.
•	Kết hợp giữa BFS và tìm kiếm cục bộ.
2.4.3. Hình ảnh GIF minh họa hoạt động
Các hình ảnh minh họa dưới đây cho thấy quá trình cải thiện lời giải của các thuật toán tìm kiếm cục bộ:
-Hill:
• simple
  ![Hill](https://github.com/user-attachments/assets/2af40e20-bc9f-45c4-a7b7-b93e5a2eee42)
• steepest accent
![Stp_Hill](https://github.com/user-attachments/assets/19c192cd-1468-4372-a2d8-9b6042617a63)
• stochastic
![Sto](https://github.com/user-attachments/assets/fc8497b5-5305-4008-a9b6-58a1428ef2f7)
- Simulated Anealing
- Beam search
  ![beamsearch](https://github.com/user-attachments/assets/dff158a6-b474-499b-8ade-63575ff27ff3)
2.4.4. Một vài nhận xét về hiệu suất
  ![image](https://github.com/user-attachments/assets/c1ea0673-0f9e-449c-9ab9-9485d73a9186)
•	Nhóm thuật toán này không đảm bảo tìm ra lời giải, nhưng nhanh và nhẹ.
•	Simulated Annealing thường có hiệu suất tốt hơn Hill Climbing.
•	Beam Search là giải pháp cân bằng, nhưng chất lượng phụ thuộc vào tham số beam width.
2.5. Các thuật toán Tìm kiếm trong môi trường phức tạp
2.5.1. Đặc điểm bài toán và cách tiếp cận
Trong môi trường thực tế, thông tin về trạng thái ban đầu có thể không chính xác hoặc không đầy đủ. Khi đó, bài toán tìm kiếm trở nên phức tạp hơn vì thuật toán không biết chính xác mình đang ở đâu – đây gọi là môi trường không xác định (non-deterministic).
Để mô phỏng điều này, đồ án đã triển khai chế độ Belief State, nơi trạng thái ban đầu không phải là một mà là một tập hợp các trạng thái khả dĩ. Mục tiêu là tìm một chuỗi hành động sao cho tất cả các trạng thái ban đầu khả dĩ đều dẫn đến trạng thái đích.
Đây là một dạng bài toán đặc biệt gọi là Conformant Planning – lập kế hoạch khi không chắc chắn hoàn toàn về trạng thái khởi đầu.
2.5.2. Các thuật toán triển khai trong nhóm
● Conformant Breadth-First Search (Conformant BFS)
•	Thuật toán mở rộng các tập hợp trạng thái (belief states) thay vì một trạng thái duy nhất.
•	Chỉ thực hiện những hành động có thể áp dụng cho mọi trạng thái trong belief state.
•	Dừng khi tất cả các trạng thái trong belief state đều đạt trạng thái đích.
2.5.3. Hình ảnh GIF minh họa hoạt động
Minh họa dưới đây mô phỏng quá trình tìm lời giải khi trạng thái ban đầu không xác định hoàn toàn:
![Con_BFS](https://github.com/user-attachments/assets/1edc1956-69e4-4ea5-8c23-6a4788c8b46f)
2.5.4. Một vài nhận xét về hiệu suất
![image](https://github.com/user-attachments/assets/9a3eeb9f-b469-4f40-a721-00d0c7a4b1e6)
•	Ưu điểm: tìm được lời giải chắc chắn trong môi trường không xác định.
•	Nhược điểm: chi phí tính toán cao vì phải duyệt tập hợp các trạng thái ở mỗi bước.
•	Thực tế chỉ áp dụng cho bài toán nhỏ (như 8-puzzle) do tính phức tạp theo cấp số nhân.
2.6. Các thuật toán Tìm kiếm trong môi trường có ràng buộc (Constraint Satisfaction Problems - CSPs)
2.6.1. Mô hình hóa 8-Puzzle như một CSP và cách tiếp cận của các thuật toán
Mặc dù 8-Puzzle thường được tiếp cận như một bài toán tìm đường trong không gian trạng thái, ta cũng có thể mô hình nó như một bài toán thỏa mãn ràng buộc (CSP), trong đó:
•	Biến (Variables): mỗi vị trí trên bảng (ô) là một biến.
•	Miền giá trị (Domain): các giá trị có thể gán cho biến là số từ 0 đến 8.
•	Ràng buộc (Constraints):
o	Mỗi số từ 0 đến 8 chỉ xuất hiện một lần.
o	Trạng thái đích phải đạt được thông qua chuỗi các trạng thái hợp lệ.
Mặc dù CSP không phải là cách tiếp cận phổ biến nhất cho 8-Puzzle, việc áp dụng các kỹ thuật CSP cho thấy khả năng sử dụng được nhiều mô hình giải quyết vấn đề khác nhau trong AI.
2.6.2. Các thuật toán/kỹ thuật triển khai trong nhóm
● Backtracking
•	Duyệt từng bước, thử gán giá trị cho từng biến.
•	Nếu xảy ra xung đột, quay lui và thử giá trị khác.
•	Là thuật toán nền tảng cho giải CSP nhưng tốc độ chậm nếu không có cải tiến.
● Forward Checking
•	Là cải tiến của backtracking.
•	Sau khi gán giá trị, loại bỏ các giá trị không hợp lệ trong miền của các biến liên quan.
•	Giúp phát hiện mâu thuẫn sớm, tăng tốc quá trình tìm kiếm.
2.6.3. Hình ảnh GIF minh họa hoạt động
Các hình ảnh minh họa dưới đây thể hiện quá trình tìm lời giải dựa trên ràng buộc và kiểm tra trước:
- Backtracking
  ![backtraking](https://github.com/user-attachments/assets/bc1569bf-7a62-4eeb-abd9-7fb4a780403f)
- Forwardchecking
  ![Forward_check](https://github.com/user-attachments/assets/30d3deb6-39dc-4f8e-9704-a45152abf927)
2.6.4. Một vài nhận xét về hiệu suất
  ![image](https://github.com/user-attachments/assets/260d97df-746a-4bbf-abff-13a768648fd5)
•	Backtracking có thể dùng như baseline để kiểm tra tính hợp lệ của trạng thái.
•	Forward Checking hoạt động tốt hơn khi kết hợp với các heuristic chọn biến/thứ tự giá trị.
2.7. Học tăng cường (Reinforcement Learning)
2.7.1. Bài toán 8-Puzzle dưới góc độ Học tăng cường
Học tăng cường (Reinforcement Learning – RL) là một phương pháp học mà agent (tác nhân) tự khám phá môi trường thông qua thử nghiệm và nhận thưởng/phạt từ hành động của mình. Mục tiêu là tìm chính sách (policy) tối ưu để tối đa hóa tổng phần thưởng theo thời gian.
Trong bài toán 8-Puzzle:
•	Agent là người chơi.
•	Trạng thái là bảng 3x3 ở mỗi thời điểm.
•	Hành động là di chuyển ô trống (0) lên/xuống/trái/phải.
•	Phần thưởng: thường là −1 cho mỗi bước, 0 khi chưa xong, và +1000 khi đạt trạng thái đích.
Bài toán trở thành một quá trình ra quyết định Markov (MDP), và ta có thể áp dụng thuật toán Q-Learning để học chính sách hành động tối ưu.
2.7.2. Thuật toán triển khai trong nhóm
● Q-Learning
•	Là thuật toán học tăng cường không cần mô hình (model-free).
•	Sử dụng bảng Q-Table để ước lượng giá trị hành động tại mỗi trạng thái.
•	Dần dần học được chiến lược tốt nhất thông qua nhiều episode thử nghiệm.
•	Cập nhật Q-Value theo công thức:
Q(s,a)←Q(s,a)+α⋅[r+γ⋅max⁡a′Q(s′,a′)−Q(s,a)]Q(s, a) \leftarrow Q(s, a) + \alpha \cdot [r + \gamma \cdot \max_{a'} Q(s', a') - Q(s, a)]Q(s,a)←Q(s,a)+α⋅[r+γ⋅a′maxQ(s′,a′)−Q(s,a)] 
Trong đó:
o	α\alphaα: learning rate
o	γ\gammaγ: discount factor
o	rrr: phần thưởng
o	s,as, as,a: trạng thái và hành động hiện tại
o	s′,a′s', a's′,a′: trạng thái và hành động tiếp theo
2.7.3. Hình ảnh GIF hoạt động
Hình ảnh bên dưới minh họa quá trình Q-Learning học dần cách giải bài toán 8-Puzzle qua nhiều lượt chơi:
- Q_learning
![Q_learning](https://github.com/user-attachments/assets/ee9f8001-c4fc-41b9-84a5-8bf0b2da273e)
2.7.4. Một vài nhận xét về hiệu suất
  ![image](https://github.com/user-attachments/assets/961c1e77-1b3d-46f3-9d3b-2ba0df2e5017)
•	Q-Learning cần rất nhiều lần thử (hàng ngàn episodes) để học chính sách tốt.
•	Với 8-Puzzle, không gian trạng thái quá lớn (≈181,000 trạng thái hợp lệ), Q-table truyền thống không khả thi trừ khi rút gọn trạng thái hoặc dùng mô hình Deep Q-Network.
•	Dù vậy, nó minh họa rõ cơ chế học từ trải nghiệm mà không cần biết trước môi trường.
3. Kết luận
Thông qua quá trình xây dựng và triển khai hệ thống giải bài toán 8-Puzzle đã đạt được nhiều mục tiêu cả về mặt lý thuyết lẫn thực hành:
•	Triển khai thành công một loạt thuật toán tìm kiếm, từ cơ bản đến nâng cao, bao gồm:
o	Tìm kiếm không có thông tin: BFS, DFS, UCS, IDDFS
o	Tìm kiếm có thông tin: A*, Greedy, IDA*
o	Tìm kiếm cục bộ: Hill Climbing, Simulated Annealing, Beam Search
o	Tìm kiếm trong môi trường phức tạp: Conformant BFS với Belief State
o	Giải bài toán ràng buộc (CSP): Backtracking, Forward Checking
o	Học tăng cường (RL): Q-Learning
•	Tạo ra một giao diện trực quan giúp người dùng tương tác dễ dàng: nhập trạng thái, chọn thuật toán, quan sát kết quả và theo dõi các bước giải dưới dạng ảnh động.
•	Mở rộng góc nhìn về bài toán 8-Puzzle: không chỉ là bài toán tìm đường, mà còn có thể tiếp cận dưới dạng CSP, lập kế hoạch không xác định, hoặc quá trình học hỏi không giám sát.
 Một số điều rút ra khi làm đồ án:
•	Không có một thuật toán "tốt nhất" cho mọi trường hợp – mỗi thuật toán phù hợp với hoàn cảnh và yêu cầu cụ thể.
•	Các thuật toán heuristic như A* tỏ ra hiệu quả nhất về tốc độ và độ chính xác khi sử dụng heuristic phù hợp.
•	Những thuật toán như Simulated Annealing hay Q-Learning có khả năng mở rộng cho các bài toán phức tạp hơn nhưng yêu cầu nhiều thời gian hoặc dữ liệu huấn luyện.


