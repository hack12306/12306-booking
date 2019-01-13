# 12306-booking
12306订票工具

## 12306booking vs 12306 vs 第三方订票平台

为什么要写一个订票工具？

1. 12306订票体验太差。验证码识别太逆天，人眼无法识别。刷新、刷新、刷新，刷到手疼。票就在那里，你就是定不上
2. 第三方订票平台太流氓。收集用户数据，还收不可接受的手续费（美其名曰技术服务费，其实就是 CPU和 RAM），最恐怖的是还要将用户数据拿到市场交易

解决了什么问题，有什么优点？
1. 两次扫码就完成了登录、查询余票、下单到支付的所有流程
2. 本地运行，不收集任何用户数据，不用输入用户密码，不用担心任何数据泄露、交易行为
3. 完全开源，没有任何黑箱操作
4. 刷新、订票流程快，先人一步抢到票
5. 支持多车次、多席别、多乘客抢票

## 使用说明

安装
```sh
pip install 12306-booking -U --user;
```
>如果使用MacOS，使用虚拟环境安装`virtualenv venv; source venv/bin/activate; pip install 12306-booking -U`

订票
```sh
12306-booking --train-date 2020-01-01 --train-names K571 --seat-types 硬卧 --from-station 北京 --to-station 麻城 --pay-channel 微信 --passengers 任正非,王石
```
> 多车次、多席别、多乘客之间用英文的','分割

## 订票流程

![订票流程](https://processon.com/chart_image/5c372ce1e4b08a7683a2798f.png)

## 订票状态机

![订票状态机](http://processon.com/chart_image/5c371a11e4b0641c83d6eb3f.png)


## 赞助

如果有帮助到你订到票，请扫描二维码赞赏我们，你的鼓励是我们持续改进优化的动力。

<img src="https://share-static.oss-cn-hangzhou.aliyuncs.com/wx/%E5%BE%AE%E4%BF%A1%E8%B5%9E%E8%B5%8F.jpg"  width="50%" height="50%" />
