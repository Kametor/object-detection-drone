# Sunum Hakkında Yazdığım Promptlar (orijinal hâliyle)

> Bu dosya benim yazdığım mesajların birebir kopyasıdır, düzeltme/özetleme yapılmamıştır.
> Kronolojik sırayla.

---

## 1 — Final sistem fikri (YOLO + ResNet + SAM3)

aklıma süper bir şey geldi final solution olarak vereceğimiz sistemde yolo + resnet olacak gibi duruyor şimdilik bu sisteme atıyorum 10 sn de bir çalışacak şekilde bir de sam3 entegre edelim ki sistemdeki anormallikleri anlamış olsun. bu onemli bunu bana hatırlar

---

## 2 — Sunuma başlama, taslak talebi

Selam claude biraz vakit geçirdim ama tekrar burdayım. son durum şu kayınpederlerdeyim ve kayınpederim imac i var. ordan yazıyorum. elimizde drive daki dosyalarımız ve github daki kodlarımız var. bugünün hedefi belli elimizdeki tüm verilerle sunuma başlamak. genel bi taslağını oturtmak ve detayları doldurmak. zaten teknik tarafta yapılacak işler belli onları olabildiğince yarın ve çarşamba günü işte yapmaya çalışıcam yaptıkça sunuma ekliyicem. haydi sunuma devam edelim. benim sunuma koyacağımız şeylerle alakalı kabaca bir planım. var. sen de dünkü vs code session ında olması lazım bir tane taslak çıkartmıştın bana. onlarla bi devam edelim.  burda akıllıca bir şey yapalım sanırım sunum yapma senin baya bi token ını yiyor. şuanda haftalık limitimizin %50 sindeyiz ve 1 saate dolacak. onun için bu 1 saati yüksek token yiyen bir şekilde ilerletebiliriz ki hakkımızı tam kullanmış olalım. benim ilk aklıma gelen sunumu sen direk oluşturma token ve zaman harcamayalım. ilk once sunumun genel içeriğini netleştirelim. sunum kaç sayfadan oluşacak. hangi bolümler yer alacak. giriş gelişme sonuç nasıl bir yapıda ilerliyicez. sunumda olmassa olmaz neler olacak. özellikle sana daha önce iletmiş olduğum ödev pdf inde bunlar zaten yazıyor bunların üstüne biz neler yapıcaz vs. aşırı promptu büyütmek istemiyorum seri bir şekilde bi ben yazayım bi sen cevap ver yapımızı kuralım

---

## 3 — Format, renkler, gerçek hayat bağlantısı (20-25 dk, kurum renkleri, fabrika örneği)

Öncelikle sunum için 20 dk olacak gibi belki biraz daha uzatıp 25 dk yapabiliriz olabildiğince seri anlatıp yapmış olduğum tüm geliştirmeleri anlatmak istiyorum. Bu anlamda bol resimli bol test sonucu çıktılı sayfalar koyalım. Dinleyenler keyifle bir film izliyormuş gibi ilgisini kaybetmeden sunumu dinlesin. Neden sonuç ilişkileri çok önemli olacak. Dinleyici bir noktada ne alaka niye bunu yaptın şimdi dememeli. Genel olarak roketsan şirketine yapacağımız bu sunumda arkaplan renginde kurum renklerini kullanalım. Pantone 7740 C
CMYK
C80 M20 Y100 K5
RGB
R58 G145 B63

 
Pantone Black C
CMYK
C0 M0 Y0 K100
RGB
R29 G29 B27

 
Pantone 429 C
CMYK
C39 M27 Y27 K6
RGB
R164 G169 B173


onun haricinde olaya direk girmeyelim diyorum bira daha verilen problemi gerçek hayata çekebilmiş bir mühendis olarak verilen bu problemi gerçek hayatla ilişkilnedirelim. Benim aklıma birçok güvenlik kamerasının olduğu bir sistemde nesne tespiti yapılması geldi. Veya büyük bir fabrikada binlerce kamera var ve ürün denetimi yapıyor diyelim. Böyle bir durumda donanımı çok yormayacak bir sistem olmalı ayrıca nesne tespitinde baktığımız nesne daha önce eğitilmemiş bir sınıfsa fabrikada yeni üretilmiş bir ciism gibi bizim bunu eğitmemiz gerekir ve her şeyi manuel etiketleyemeyiz. Bunu kısaca anladığımızı göstericek bir sayda olsun derim. Devam edicem bu bir sayfa

---

## 4 — Eski taslağı açma isteği

genel taslağın fena değil ama değiştirmek istediğim bir çok şey var tabiki eklemek istediğim de. ilk olarak bu senin yaptığın dünkü sunumu bi açabilir miyiz onda da güzel şeyler vardı onlara da bi baklaım

---

## 5 — Repo linki

https://github.com/Kametor/object-detection-drone/commits/main/ sen de incele ama commit lerde bir sunum göremedim

---

## 6 — Kendi yapımı aktarma: dil, renk, açılış slaytı, konuşmacı tanıtımı

o zaman ben direk kendi aklımdaki yapıyı sana aktarayım daha sonra burdan optimize ederek ilerleriz. bu sunumda aslında yapmış olduğumuz çalışmaları bizden ne istendi biz nasıl bir yapı düşündük neler yaptık nasıl yaptık ilerlerken önemli gördüğümüz nelere dikkat ettik vb konuları akıcı bir şekilde sunmaya çalışıcaz. genel olarak sunumun metin dili ingilizce olacak. arkaplanlarda roketsanın renklerini kullanabiliriz belki yeşil tonlarında hoş bir arkaplan olabilir profesyonel modern bir hava katar. ilk sayfamızda konumuzu yazalım. konuya çalışan kişi olarak benim Mehmet Recep Aşkar ismim olsun altına Computer Vision Engineer diyebiliriz sanki. Yine bu sayfada bir köşe de roketsan logosu konulabilir. konunun ilgili resimleri olarak belki kendi çalışmalarımızdan ki bu daha emek gösterir resimler koyabiliriz atıyorum tespit ettiğimiz insanların olduğu bbox ların olduğu bir resim gibi vs. tabi sunumları düşünürken aslında benim konuşma metinlerimi de düşünmek lazım yani sunumun akışı benim nasıl konuşacağım gibi sonuçta sunum dediğimiz şey dinleyicilerin ne gördüğü benim anlattıklarımsa ne duydukları ikisinin senkron gitmesi lazım. bu sayfada ben bi giriş yaparım hello my name is mehmet recep aşkar ı am electric and electronic engineer graduated from middle east technical university from 2022 ı am currently working in mke as a computer vision engineer in the areas visual navigation and object detection and tracking. today ı will present you my solutions on object detection in limited data tarzı bir şey derim. sonrasında açılışı yapmış oluruz. artık konumuza başlama vakti burdaki kritik şey konuyu en baştan temizce anlamışmıyız anlatabiliyor muyuz. konu aslında belli nesne tespiti ancak ödevde de soylendiği gibi elimizde küçük ve labellanmamış bir veri seti var. yani burdan bir çıkarım yapmak model eğitmek işin ana problemi bu kıstaslar içerisinde odev bize diyorki sen bu veriyi nasıl kullanıcaksın nasıl mimariler ile probleme yaklaşıcaksın. bu anlamda ikinci sayfa problem definition tarafı olabilir. ilk ödevin bizden istediği şeyi direk anlatalım benim sana yazdığım tarz gibi. ama bunu gerçek hayatlada ilişkilendirelim. diyelim ki aslında burdaki motivasyon gerçek hayattada görebileceğimiz bir şey ornek verelim diyelim ki yüzlerce roketsan da kamera var peki burdaki veriler akıllı bir şekilde işlenirse aynı anda binlerce veri binlerce tespit edilecek nesne. yeni bir nesnede etiketlenmemiş çok büyük verilerde modellerin eğitimi nasıl olacak? ya da roketsanın fabrikaları birçok fabrikasında endüstri 5.0 ile birçok computer vision ile akıllı sistemler kurulabilir ürün sayımları iş güvenliği uygulamaları vs. aslında veri etiketli gelmez ve modellerin bu ortamlarda da nesne tespiti yapması gerekebilir. bu örnekler olayı ne kadar gerçek hayatla ilişkilendirmişiz bunu gösterecek. ikinci sunum aslında kısa ve öz verdikleri konunun teknik olayı ve bizim onu gerçek hayatla ilişkili şekilde motivasyonuyla algılama şeklimizi çok net göstermiş olacak. olabildiğince her sayfayı contexine uygun dolu dolu hazırlamaya çalışalım. vaktimiz az ama anlatacağımız çok şey var. bu sayede seri seri sunumu anlatır geçerim. şimdi adım adım gidelim ki senin de contexin dolmasın. bence sen bu dosyaya sunum içeriği şeklinde bu bilgileri özet olarak yaz ki hep onun üzerinden giderek güncelleyelim. sonra diğer adımlardaki şeylere geçicem

---

## 7 — Slayt 1/2 düzeltmeleri, konuşma dili, hedef sınıf gerekçesi (slayt 3)

konuşma metnimiz de ingilizce olacak. sunum bitsin onun da metnini genel hattıyla birlikte hazırlarız ben bi kendi kendime okurum. genel tasarım kuralı doğru değil o sayfanın ne anlatığına göre değişir.
birinci sayfa: roketsan logosu sağ üstte olsun.  arka plan temiz olsun koyacağımız resimler blurlu arkada olmasın çok dandik bir hava verir. biz onları çok arkaplanı kaplamadan 3-4 resmi küçük küçük etrafa koyabiliriz. bu içerik metni vs codda yaptığın sunumda baya güzeldi onları ben o sunumla merge lerim. 
slayt 2: archieve is large doğru değil aslında verdikleri datasette 13 kısa video var. veri de az label da yok.  b kısmı güzel olmuş oraya güvenlik kameralarını da koy. 
bu arada ödev pdf imizi tekrar okuduğumuzda aslında sunumda beklenilen şeyler çok net biz yapmış olduğumuz çalışmalar ile bunları doldurmamız yeterli.

Sonuçların Sunulması 
• Seçilen hedef ve kullanılan veri bölümü • Veri hazırlama ve etiketleme stratejisi • Başlangıç yaklaşımı • Alternatif yaklaşım • Yaklaşımların nicel ve nitel karşılaştırması • Başarılı, başarısız ve belirsiz sonuçlar • Hata analizi • Yaklaşımın güçlü ve zayıf yönleri • Hesaplama maliyeti Kullanılan değerlendirme yöntemi ve metriklerin neden tercih edildiği açıklanmalıdır. 

Sunum sırasında şunların da gösterimi beklenmektedir: • Çalıştırılabilir Google Colab notebook veya kod deposu • Kurulum ve çalıştırma adımlarını içeren README • Nicel sonuç tablosu • Başarılı ve başarısız sonuç örnekleri • Kullanılan kaynakların listesi • Varsa sonuç videosu 

Değerlendirme • Problemin doğru tanımlanması • Veri hazırlama stratejisi • Teknik yaklaşımın doğruluğu • Farklı çözüm stratejilerinin araştırılması ve karşılaştırılması • Yapılan deneylerin kalitesi • Hata analizi ve teknik yorumlar • Sonuçların doğruluğu ve sunumu • Kod kalitesi ve tekrar üretilebilirlik

o zaman slayt 3 de seçilen hedef ve kullanılan veri bölümü denilmiş. burda veriyi nasıl okuduğumuz ilk önce bi anlatalım. tabi burdaki nicel değerler benim aklımda değil onu vs code la tekrar bakarız. ama 13 tane videomuz vardı. vc code da biz bu videolarda hangi nesneler var backgroundlarında neler var vb çok güzel bir analiz yaparak tablo oluşturmuştuk onu anlatırım. sonuçta bu tabloyla aslında veriyi doğru bir şekilde okuduğumuzu anlatmış oluruz.  seçilen veri olarak 13 videonun 11 inde sanırım insan vardı insanın en fazla nesne olması nedeniyle seçtiğimizi hem eğitim sırasında train veri setinin hem doğrulama aşamsında test verisetinin bu sayede daha genellenebilir olacağını düşündüğümüzden insan seçtiğimizi anlatmış oluruz. kullanılan veri bölümünde burdaki videoları test train ve val için nasıl ayırdığımızdan oranlarından bunları ne amaçla kullanacağımızdan bahsedelim. kullanılan veri bölümü sanırım bu anlamda anlatmış oluruz. bu sayfada doyurucu olmuş olur. tabi burda bu insanların olduğu frame lerden henüz bbox atmadığımız boş halleriyle görsel olarak da doldururuz. bi değerlendir sonra tekrar ilerliyelim

---

## 8 — Slayt 3/4 ayrımı, split gerekçesi (video seviyesi vs frame seviyesi)

pardon doğru diyosun. ilk adımdaki kullanılan veri bölümü demiş zaten o zaman dediğin gibi biz sadece orda neden insan ve veri setindenki hangi videoları bu amaçla kullandık bunu cevaplandırız.  slayt 4 te veri hazırlama ve etiketleme stratejisi kısmında ise veriyi nasıl ayırdığımızı burda anlatırız. train test val olayını vs. etiketleme kısmı tabi tek sayfa olmayabilir çünkü cvatla etiketleyip geçmedik orda sam3 kullandığımızı anlatıcaz. belki test veri setinin çok kıymetli olduğunu ve bu nedenle cvat ile elle manuel etiketlediğimiz soyleriz bu slayt 4 te. sonrasında train için otomatik bir etiketleme metoduna ihtiyaç duyudlduğunu ve sam3 ü kullandığımızı slayt 5 te anlatırız. bir sayfa ayırmamız güzel olabilir buna. yine burda sam3 ün hem çıktı resimlerini koyarız hem de numerik olarak da koyabileceğimiz şeyleri yazarız atıyorum inference time vb. sonuçta şu akla gelir genel olarak etiketleme başarısı nasıldı ve ne kadar sürede ne kadar etiketleme yapabiliyor burda aldığımız bir hata olan gölge tespitinden bahsedebiliriz sornasında thresholdunu arttırdığımızdan vs. bu çok güzel olur.
slayt 3 için envanter olayını doğru diyorsun koca bir tablo koymayalım repo da olduğundan bahsedilebilir biz özet bilgiyi verebiliriz atıyorum en fazla video da bulunan nesne insandı gibi. tabi birazda sayısal değer vermek güzel olur. 
4 . slaytta test ve train in değerinden bahsedelim tamamdır. test e yeterli video seçmeliydik ki methotlarımızı yeterince genel bir contexte değerlendirmiş olalım. train için yeterli adette video seçmeliydikki tek bir domain üzerine video eğitmeyelim. ayrıca 4. slaytta çok önemli bir bilgi de verelim biz test train val ı videoların frameleri bazında yapmadık oyle yapsaydık aynı domain içinde kalmış olurlardı bunları biz video seviyesinde yapıp ayrı ayrı videolardan seçtik bu da önemli bir bilgi. 
 lütfen bu bilgileri de ekle

---

## 9 — Literatür/atıf isteği

şimdi aklıma gelen önemli bir şey sunumda literatürde yapılan geliştirmelerle ilgili de bilgi kullandık gösterebilmek için en sonuna veya belli yerler belli makalelerden alıntı yapmamız çok profesyonel olur. bunu da ekle lütfen. bu arada slayt 5 e kadar okudum baya güzel oldu şuanda sayfalarımız süper. şimdilik burda çalışmamı durdurucam. kendi evime geçince tekrar çalışırız. vs code u açarım ordaki bilgilerimizle daha hızlı ilerleriz sağol claude

---

## 10 — SAM3'ün test setinde doğrulanması (slayt 5 eklemesi)

sam3 performansını test veri setinde de çalıştırarak aslında manuel etiketlerimiz ile karşılaştırdığımızı ve gerçekten tatmin edince güvendiğimiz slayt 5 te soyle.
