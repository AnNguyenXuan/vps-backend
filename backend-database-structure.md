Table users {
    id INT [pk, increment]
    username VARCHAR [not null, unique]
    email VARCHAR [not null, unique]
    password VARCHAR [not null]
    phone VARCHAR
    address VARCHAR
    is_active BOOLEAN [default: true]
    created_at TIMESTAMP [default: 'CURRENT_TIMESTAMP']
    updated_at TIMESTAMP [default: 'CURRENT_TIMESTAMP']
}

Table permissions {
    id INT [pk, increment]
    name VARCHAR [not null, unique]
    description TEXT
}

Table groups {
    id INT [pk, increment]
    name VARCHAR [not null, unique]
    description TEXT
}

Table group_members {
    user_id INT [ref: > users.id]
    group_id INT [ref: > groups.id]
    indexes {
        (user_id, group_id) [unique]
    }
}

Table group_permissions {
    id INT [pk, increment]
    group_id INT [ref: > groups.id]
    permission_id INT [ref: > permissions.id]
    target_id INT
    is_active BOOLEAN [default: true]
    is_denied BOOLEAN [default: false]
}

Table user_permissions {
    id INT [pk, increment]
    user_id INT [ref: > users.id]
    permission_id INT [ref: > permissions.id]
    target_id INT
    is_active BOOLEAN [default: true]
    is_denied BOOLEAN [default: false]
}

Table categories {
    id INT [pk, increment]
    name VARCHAR [not null, unique]
    description TEXT
    parent_id INT [ref: > categories.id]
}

Table products {
    id INT [pk, increment]
    name VARCHAR [not null]
    description TEXT
    location_address VARCHAR [not null]
    category_id INT [ref: > categories.id]
    popularity INT
    created_at TIMESTAMP [default: 'CURRENT_TIMESTAMP']
    updated_at TIMESTAMP [default: 'CURRENT_TIMESTAMP']
    is_active BOOLEAN [default: true]
    is_delete BOOLEAN [default: true]
}

Table product_attributes {
    id INT [pk, increment]
    product_id INT [ref: > products.id]
    name VARCHAR(255) [not null]
}

Table product_attribute_values {
    id INT [pk, increment]
    attribute_id INT [ref: > product_attributes.id]
    value VARCHAR(255) [not null]
}

Table product_options {
    id INT [pk, increment]
    product_id INT [ref: > products.id]
    price DECIMAL(10,2) [not null]
    stock INT [not null]
}

Table product_option_values {
    id INT [pk, increment]
    option_id INT [ref: > product_options.id]
    attribute_value_id INT [ref: > product_attribute_values.id]
}

Table cart {
    id INT [pk, increment]
    user_id INT [ref: > users.id]
    product_option_id INT [ref: > product_options.id]
    quantity INT [default: 1]
    created_at TIMESTAMP [default: 'CURRENT_TIMESTAMP']
}

Table wishlist {
    id INT [pk, increment]
    user_id INT [ref: > users.id]
    product_option_id INT [ref: > product_options.id]
    created_at TIMESTAMP [default: 'CURRENT_TIMESTAMP']
}

Table coupons {
    id INT [pk, increment]
    code VARCHAR [not null, unique]
    discount DECIMAL [not null]
    start_date TIMESTAMP [not null]
    end_date TIMESTAMP [not null]
    is_active BOOLEAN [default: true]
}

Table orders {
    id INT [pk, increment]
    user_id INT [ref: > users.id]
    total_amount DECIMAL [not null]
    payment_method VARCHAR [not null]
    shipping_status VARCHAR [not null]
    payment_status VARCHAR [not null]
    shipping_fee DECIMAL [default: 0.00]
    discount DECIMAL [default: 0.00]
    coupon_id INT [ref: > coupons.id]
    created_at TIMESTAMP [default: 'CURRENT_TIMESTAMP']
    updated_at TIMESTAMP [default: 'CURRENT_TIMESTAMP']
}

Table order_details {
    id INT [pk, increment]
    order_id INT [ref: > orders.id]
    product_option_id INT [ref: > product_options.id]
    quantity INT [not null]
    price DECIMAL [not null]
}

Table reviews {
    id INT [pk, increment]
    product_id INT [ref: > products.id]
    user_id INT [ref: > users.id]
    rating INT [not null]
    comment TEXT
    is_approved BOOLEAN [default: false]
    created_at TIMESTAMP [default: 'CURRENT_TIMESTAMP']
}

Table notifications {
    id INT [pk, increment]
    user_id INT [ref: > users.id]
    title VARCHAR [not null]
    message TEXT [not null]
    type ENUM('email', 'sms', 'push') [default: 'push']
    is_read BOOLEAN [default: false]
    created_at TIMESTAMP [default: 'CURRENT_TIMESTAMP']
}

Table refresh_tokens {
    id VARCHAR(64) [pk, not null]
    expires_at TIMESTAMP [not null]
}

Table blacklist_tokens {
    id VARCHAR(64) [pk, not null]
    expires_at TIMESTAMP [not null]
}

Table list_tables {
    table_name VARCHAR [pk]
    description TEXT
}

Table files {
    id INT [pk, increment]
    user_id INT [ref: > users.id]
    file_name VARCHAR [not null]
    file_path VARCHAR [not null]
    file_size INT [not null]
    sort INT
    uploaded_at TIMESTAMP [default: 'CURRENT_TIMESTAMP']
    is_active BOOLEAN [default: true]
    list_tables VARCHAR [ref: > list_tables.table_name]
    description TEXT
}

Table interactions {
    id INT [pk, increment]
    user_id INT [ref: > users.id]
    product_id INT [ref: > products.id]
    action_id INT [ref: > actions.id]
    created_at DATETIME [default: 'CURRENT_TIMESTAMP']
}

Table actions {
    id INT [pk, increment]
    name VARCHAR [not null, unique]
    description TEXT
    score INT [default: 0]
}




mô tả, giải thích:

t chỉ mô tả, giải thích một số chỗ đọc còn mơ hồ.

bảng user quá rõ ràng rồi

bảng permissions lưu giữ các quyền hạn người dùng. 

danh sách quyền hạn như sau:

        $permissions = [
            // Quản lý người dùng
            'view_users' => 'Xem danh sách người dùng',
            'view_user_details' => 'Xem chi tiết người dùng',
            'create_user' => 'Tạo người dùng mới',
            'edit_user' => 'Chỉnh sửa thông tin người dùng',
            'delete_user' => 'Xóa người dùng',
            'activate_deactivate_user' => 'Kích hoạt/khóa người dùng',
            'manage_user_permissions' => 'Quản lý phân quyền cá nhân',

            // Quản lý nhóm
            'view_groups' => 'Xem danh sách nhóm',
            'view_group_details' => 'Xem chi tiết nhóm',
            'create_group' => 'Tạo nhóm mới',
            'edit_group' => 'Chỉnh sửa thông tin nhóm',
            'delete_group' => 'Xóa nhóm',
            'manage_group_members' => 'Quản lý thành viên nhóm',
            'manage_group_permissions' => 'Quản lý phân quyền nhóm',

            // Quản lý quyền
            'view_permissions' => 'Xem danh sách quyền',
            'create_permission' => 'Tạo quyền mới',
            'edit_permission' => 'Chỉnh sửa quyền',
            'delete_permission' => 'Xóa quyền',

            // Quản lý sản phẩm
            'view_products' => 'Xem danh sách sản phẩm',
            'view_product_details' => 'Xem chi tiết sản phẩm',
            'create_product' => 'Tạo sản phẩm mới',
            'edit_product' => 'Chỉnh sửa thông tin sản phẩm',
            'delete_product' => 'Xóa sản phẩm',
            'manage_featured_products' => 'Quản lý sản phẩm nổi bật',
            'manage_product_stock' => 'Quản lý số lượng tồn kho',

            // Quản lý danh mục
            'view_categories' => 'Xem danh sách danh mục',
            'create_category' => 'Tạo danh mục mới',
            'edit_category' => 'Chỉnh sửa danh mục',
            'delete_category' => 'Xóa danh mục',

            // Quản lý giỏ hàng
            'view_carts' => 'Xem giỏ hàng của người dùng',
            'edit_carts' => 'Chỉnh sửa giỏ hàng của người dùng',
            'delete_carts' => 'Xóa giỏ hàng của người dùng',

            // Quản lý danh sách yêu thích
            'view_wishlists' => 'Xem danh sách yêu thích của người dùng',
            'edit_wishlists' => 'Chỉnh sửa danh sách yêu thích của người dùng',
            'delete_wishlists' => 'Xóa sản phẩm khỏi danh sách yêu thích',

            // Quản lý mã giảm giá
            'view_coupons' => 'Xem danh sách mã giảm giá',
            'create_coupon' => 'Tạo mã giảm giá mới',
            'edit_coupon' => 'Chỉnh sửa mã giảm giá',
            'delete_coupon' => 'Xóa mã giảm giá',
            'activate_deactivate_coupon' => 'Kích hoạt/Vô hiệu hóa mã giảm giá',

            // Quản lý đơn hàng
            'view_orders' => 'Xem danh sách đơn hàng',
            'view_order_details' => 'Xem chi tiết đơn hàng',
            'update_shipping_status' => 'Cập nhật trạng thái vận chuyển',
            'update_payment_status' => 'Cập nhật trạng thái thanh toán',
            'delete_order' => 'Xóa đơn hàng',

            // Quản lý đánh giá sản phẩm
            'view_reviews' => 'Xem danh sách đánh giá',
            'approve_disapprove_review' => 'Duyệt/Không duyệt đánh giá',
            'delete_review' => 'Xóa đánh giá',

            // Quản lý toàn hệ thống
            'access_admin_dashboard' => 'Truy cập Dashboard quản trị',
            'manage_system_settings' => 'Quản lý cấu hình hệ thống',
            'view_system_logs' => 'Quản lý nhật ký hệ thống',
        ];

bảng groups:

nhóm người dùng lại để dễ làm việc, quản lí. mục đích đầu tiên của t là để phân quyền cho nhóm người
ví dụ cho nhóm admin, mọi quyền. nó chứa danh sách các nhóm

bảng group_members:

cho người vào nhóm. nó chứa 2 khóa ngoại trỏ đến users và groups. nó là sự liên kết giữa người dùng và nhóm
nếu có liên kết có nghĩa là người dùng thuộc nhóm đó 

bảng user_permissions:

phân quyền cho từng người dùng
user_id là người được cấp quyền
permission_id trỏ đến cái quyền đó
target_id cái này là để phân quyền chi tiết. 
hàm này trong code function hasPermission(User $user, string $permissionName, ?int $targetId = null): bool
nếu target_id là null thì người dùng đó được cấp full quyền đó
nếu là một giá trị nào đó. ví dụ như admin thì target_id là null nhưng trưởng của một groups thì target_id là id của groups chẳng hạn
nó đặt hàm kia đặt trong code để phân quyền chi tiết.
is_active: là cái cài đặt quyền này có được bật lên hay không. kiểu ông admin setup xong để đó cho nhớ nhưng chưa muốn cấp quyền ngay chảng hạn 
is_denied là người dùng này bị từ chối quyền này khay không. nếu bị từ chối thì đâu đó người dùng này được cấp quyền thì vẫn là từ chối.
ví dụ như ở trong 1 nhóm thì ăn theo quyền nhóm là được cấp. nhưng chat với 1 bạn gái bị ăn block thì chịu.


bảng group_permissions cũng tương tự bảng kia thôi. 


bảng categories:
nó là danh mục sản phẩm 
ví dụ:
thời trang
quần
áo
dép
áo đông xuân
dép lê
dép bưởi
có cột parent_id trỏ đến chính bảng này
mục đích ư. để phân cấp cha con
thời trang : {
    quần
    áo {
        áo đông xuân 
    }
    dép {
        dép lê 
        dép bưởi 
    }
}

truy xuất dép lê thì nó sẽ ra như này: thời trang/dép/dép lê


bảng products:

location_address một thương hiệu có thể có nhiều cơ sở. đây là địa chỉ của cơ sở đang bán sản phẩm đó 
popularity chấm điểm nổi tiếng của sản phẩm. nó được kết hợp với lịch sử mua sắm người dùng để đưa ra gợi ý sản phẩm cho người dùng và sắp xếp thứ hạng tìm kiếm
nó có thể được hiệu chỉnh bằng dữ liệu người dùng tương tác.
còn như nào á. => học máy 

các bảng product_attributes, product_attribute_values, product_options, product_option_values

các bảng này sinh ra để làm gì:
việc một mặt hàng có quá nhiều sự lựa chọn. size, màu sắc kích thước ... để phục vụ vấn đề đấy thì sinh ra mấy bảng này 
bảng product_attributes chứa thông tin các sự lựa chọn: size, màu sắc, ...
bảng product_attribute_values lưu các giá trị của các đặc tinh trên. ví dụ như size 40, 41,42 thì attribute_id trỏ đến bản ghi size, value là 40, 41, 42 ...

mỗi product_attributes tương ứng cho mỗi hàng lựa chọn. mỗi product_attribute_values tương ứng với một cột trong hàng
khi người dùng chọn đủ tất cả các hàng. nghĩa là mỗi product_attributes thì đã chọn được một product_attribute_values
khi người dùng chọn đủ. đã có một tổ hợp hoàn chỉnh các lựa chọn mỗi hàng thì sẽ ứng được với một sản phẩm cần tìm
như dép màu đỏ size 42.

thì khi đó sẽ có giá, cho sự lựa chọn đó. và bảng product_options sẽ lưu giữ điều đó. 
số lượng tất cả các hàng trên nhân với nhau thì product_options cũng nhiều đấy. 
trong code cách tìm ra một sự lựa chọn là như thế nào. đầu tiên ta có id sản phẩm. là xác định được sẳn phẩm
sau đó từ sản phẩm tả quét xem nó có những sự lựa chọn nào (product_attributes). sau quét trong những sự lựa chọn ấy người dùng chọn cái gì (khi người dùng nhấn vào ở frontend là đã gán được values cho product_options rồi)
tất cả các sự lựa chọn (màu săc, kích thước ...) sẽ xác định được duy nhất một product_options
vì product_options và product_attribute_values là quan hệ nhiều nhiều nên ta cần một bảng nối giữa chúng là product_option_values

ê. có một vấn đề. nếu sản phẩm k có sự lựa chọn nào thì sao. như shop nào muốn ghi tên sản phẩm là "thẻ cào điện thoại viettel 10" thay vì đặt tên "thẻ cào điện thoại" cho có sự lựa chọn
cách giải quyết là. vẫn tạo 1 bản ghi trong product_options như bình thường. k có sự lựa chọn nghĩa là có 1 sự lựa chọn duy nhất. nghe vẫn hợp lí mà đúng không.
khi đó product_attributes là rỗng. chưng trình chạy là. biết sản phẩm, quét các thuộc tính sản phẩm (product_attributes) nó là rỗng thì select cái product_options với product_id thì nó có duy nhất 1 cái thôi. vấn đề được giải quyết.
nếu có các sự lựa chọn khác ngoài 1 lựa chọn duy nhất thì xóa bản ghi vừa rồi đi là xong. thêm bản ghi mới.

nếu sản phẩm có rất nhiều sự lựa chọn. và nhập vào nó mất rất nhiều công sức và lười nhập thì sao
về số lượng. thì bắt buộc là phải biết sản phầm loại này loại kia có bao nhiêu rồi, không thể lười nhập được. nếu k muốn nhập thì đừng bán 
về giá. các sự lựa chọn có giá giống nhau. thì phía front thiết kế cho họ nhập 1 lần.
sau đó điền tự động. nếu họ bấm ok thì lưu. điền tự động rồi nếu họ muốn giá khác thì nhấn vào trường điền giá đổi.


bảng cart:
product_option_id trỏ đến từng sự lựa chọn của sản phẩm
quantity số lượng sản phẩm trong giỏ hàng. t có nhớ thầy toàn hỏi mình là làm sao các em xác định được số hàng trong kho. thì số hàng hiện tại = số hàng trước đó - đơn đặt hàng thôi. nếu khách hàng hủy đơn thì lại cộng lại. shopee họ cũng làm vậy. t thử rồi. còn quản lí kho chi tiết thì chắc phải có phần mềm khác. hoặc là phát triển cái này thêm. mà như bọn shopee nó là sàn thì không có kho đâu. vì sản phẩm ở mỗi shop nên kho k tồn tại

bảng wishlist:
này do thằng An nghĩ ra. cho nó giả thích. t nghĩ products đã có cột popularity và người dùng đã có giỏ hàng rồi thì thêm cái này làm gì t cũng k rõ lắm.

bảng coupons:
chắc k cần giải thích 


bảng orders:
đại diện cho một đơn hàng
total_amount cộng số tiền ngay từ thời điểm khách hàng bấm nút đặt hàng.
thầy toàn có hỏi bọn em tính thế nào. cộng lại thế các mặt hàng thay đổi thì sao.
t cũng k rõ lắm sao thầy đặt mấy câu hỏi này. vì cái này là bản ghi. và nó ghi lại rồi. chứ có tính nữa đâu. nên nó k thay đổi. 
payment_method phương thức thanh toán thì nay có COD hay nhiêu dịch vụ thanh toán. họ lo hết cho rồi. nên chả cần code gì. cần gọi API của họ để thanh toán và tra vị trí đơn hàng thôi
thích thì sau cho cái trạng thái vạn chuyển nó là một bản ghi để người dùng xem được lịch sử di chuyển thay vì chỉ xem được trạng thái hiện tại. nhưng database to lắm rồi. t k muốn to thêm.


bảng order_details là lưu thông tin chi tiết của từng sản phẩm trong đơn hàng thôi.


bảng reviews thì. haizz lười giải thích. đọc là hiểu mà. 


notifications là lưu lịch sử đã thông báo cho người dùng. gửi qua email hay tin nhắn điện thoại chẳng hạn


bảng list_tables là liệt kê tên của tất cả các bảng trong cơ sở dữ liệu này. nó phúc vụ cho nhiều việc trong tương lai. nhưng hiện tại nó phúc vụ cho bảng file.


bảng file:

rất nhiều thứ cần dùng đến file. mối quan hệ của file và các thực thể khác là nhiều mỗi thực thể khác có nhiều file. và hiện tại t đang thiết kế một file chỉ ứng với một thực thể khác. nhiều nhiều thì phát triển sau.
mối quan hệ một nhiều thì khóa ngoại đặt ở đâu. đặt ở bảng nhiều rồi. ví dụ đặt ở bảng 1 nhá. chẳng lẽ 1 sẳn phẩm đặt 10 trường ghi file. thế là bắt buộc 1 sản phẩm có 10 cái ảnh, video. ????
hay đặt id của ảnh, video trong 1 đoạn text rồi sau xử lí chuỗi để tách nó ra thành nhiều id. thôi tốc độ xử lí chuỗi chậm hơn tốc độ truy vấn cơ sở dữ liệu rất nhiều, và cách này làm mất đi tích ưu việt của database.

mối quan hệ một nhiều thì khóa ngoại thì khóa ngoại thường đặt ở bảng nhiều. thế là bảng file. nhưng bảng file k thể tạo ra một đống khóa ngoại được. và nó dùng 1 còn các cái khác là null. rất k nên thiết kế kiểu này.

vậy cách giải quyết là trong bảng file, tạo ra 1 cột ghi tên bảng và 1 cột là id của bản ghi trong bảng đó. cách này hợp lí.
để nhập liệu k bị lỗi thì cột tên bảng nên để dạng enum. nhưng nó cũng khó mở rộng. thôi thì tạo ra một bảng mới là list_tables. nó sẽ giải quyết được vấn đề này.

bảng permissions cũng kiểu na ná như bảng list_tables. 

file_path là lưu đường đẫn file. tên file được tạo bởi 32 kí tự. ở /public/data/thư mục con 1(2 chữ cái đầu trong tên)/thư mục con 2(2 chữ cái tiếp theo)/tên thật(phần còn lại của tên ban đầu)
tại sao k để file có tên như ban đầu mà phải đổi. vì nó tạo ra 1 lỗ hổng bảo mật. hacker tạo ra 1 file thực thi. nếu họ biết được địa chỉ file và bằng cách nào đó kích hoạt được file thực thi vì biết vị trí của nó. thì khá rủi ro. đây hạn chế được phần nào việc tấn công.
(số chữ + số lượng số)^32 thì rất nhiều. hơn rất rất nhiều số hạt cát trên trái đất này nên k lo trùng nhé.


bảng interactions và actions lưu lịch sử người dùng. nó dùng cho nhiều mục đính. t định dùng để gợi ý sản phẩm cho người dùng.

nhưng an bảo thôi. cho mấy sản phẩm vào. random ngẫu nhiên. thế là xong. đăng nào thầy cũng chỉ xem 1 lần. làm chi tiết quá cũng có ai thấy được đâu. lươn tí là được. các nhóm khác nó đặt sản phẩm ở nguyên một vị trí mà không thay đổi luôn cơ. nếu muốn đổi sản phẩm chắc vào code sửa rồi start lại phần hệ thống. NHƯNG THẦY CHỈ COI 1 LẦN. nên backend có xịn sò thế nào mà frontend phế thì điểm cũng thấp thôi. nên thôi. 2 bảng này để làm màu chứ k code.


refresh_tokens: 

refresh tokens có rất nhiều trường dữ liệu và được mã hóa. chỉ cần lưu id của của refresh tokens là đủ. và lưu ngày hết hạn để xóa đi trong bảng này tránh lãng phí bộ nhớ
lư refresh tokens để tăng tính bảo mật. 

blacklist_tokens:
khi đăng xuất thì lưu id của Access Token lại như cái kia. nào hết hạn cũng xóa. vì việc đăng xuất ít hơn rất nhiều so với số phiên đang hoạt động nên chỉ cần lưu những cái đăng xuất
còn duy trì phiên nó nằm ở chính cái token chứ hệ thống không lưu phiên đăng nhập (dùng JWT)