**WD-XL Lubrifont**

# Updates

## Unreleased

- Added Polish, Czech, Slovak, Romanian and Turkish letters: `ĄąĘęŚśŹźŻż ĎďŘřŤťŮů ĹĺĽľŔŕ ȘșȚțŞşŢţ ĞğİĖė` (Ď ď Ľ ľ ť with the apostrophe-style caron, Ș ș Ț ț with comma below and Ş ş Ţ ţ with cedilla), with mark anchors and kerning (`sources/add_central_european.py`)

- Opened up the overall letter spacing of Latin, Greek and Cyrillic letters, digits and Western punctuation by 12 units on each side (24 units between two letters; the word space grows by the same amount). CJK characters and full-width forms are unchanged (`sources/track.py`)

## Ver 2.300; 20261023

- Respaced the Latin and Cyrillic letters: diagonal and open capitals (`А Ж Х У Ф A X Z L` …) and loose lowercase (`д т f t s` …) tightened, `Я` and `ї ï` loosened on their tight side, and Latin/Cyrillic straight letters made consistent; accented letters follow their base letter (`sources/respace.py`)

- Added kerning (`kern`) for Latin and Cyrillic letters and punctuation, e.g. `Та Гл ГА LT AV Yo P.` (`sources/autokern.py`, values in `sources/kerning.txt`)

- Added Ukrainian `ЄєІіЇїҐґ` and Belarusian `Ўў` Cyrillic letters, with `mark` anchors for combining accents (`sources/add_ukrainian_belarusian.py`)

## Ver 2.200; 20261023

- Added `mark` anchors to Cyrillic letters and `ĆćČčĐđ` so combining stress accents (e.g. `е́ о́ и́`) sit above the letter (`sources/add_mark_anchors.py`)

- Redesigned `7` with a full-width diagonal stem so it no longer reads as `1` or a mirrored `Г` (also `７⁷₇⅞`; `sources/diagonal_seven.py`)

- Zero now has a centre dot so it cannot be confused with the letter `O`/`О` (also `⁰₀０`; `sources/dotted_zero.py`)

- Added Macedonian Cyrillic letters `ЃѓЅѕЈјЉљЊњЌќЏџ` and the stressed `ЀѐЍѝ` (built from existing glyphs with `sources/add_macedonian_cyrillic.py`)

- Added Croatian/Bosnian/Serbian Latin `ĆćČčĐđ` and Serbian Cyrillic `ЂђЋћ`

- Added technical symbols: `⌀∅∆↔↕↖↗↘↙⇐⇒⇔✓✗▼▽⁰⁵⁶⁷⁸⁹⁻₀₁₂₃₄₅₆₇₈₉⅓⅔⅛⅜⅝⅞` (`sources/add_extra_glyphs.py`)

## Ver 2.100; 20250331

- <details>
    <summary>Added 1718 hanzi, completing all hanzi in the Table of General Standard Chinese Characters, the Modern Chinese General Character List, the <a href="https://github.com/ichitenfont/suppchara">Hong Kong Supplementary Character List v1.8</a>, the <a href="https://github.com/justfont/jf7000">jf7000 Core Character Set v0.9</a> and the <a href="https://github.com/NightFurySL2001/cjktables/blob/master/china/foundry/fangzheng_jianfan.txt">Founder Simplified–Traditional list</a></summary>
    <p>

    - `丏匜厾玕玙㧐芼旸牤沨纴玡玭玠玦拤㧟茓茀杻呣䏝𬉼㤘垱挦柈𠳐眊饸饹疭闿羑浕恓牁珰琤栟眬鸮䥽盉牂埵棁秾鸻馃郿琫揳塆靰靸雱睄嵖媭鲀颎湉愔祾翚跐鹐滫滃滪璈摽靿僰豨䁖嘡魆鋆踒𥻗熜璠縠嚄螠䦃膙澥璪鞡鞬罽鳀鞧鹮霨㸆臜瓘齉𠙶毌邘圢冮汈𬣙圲圫𨙸屼癿邠𬇕汋䜣讻𬣞𬘓玒玓玘玚刬𫭟扽𫭢坋扺㧑苉芠𫇭杕杄轪𫐄坒旴旵㕮𫵷岠呇觃伾㑇伭佁飏汧𣲘𣲗沄𬇙汭㳇沇忳忺𬣡祃诇邲诐𫸩岊䢺妧妘𨚕纮驲𫘜𬘘𫘝纼玤玞玱邽邿坰坬坽弆䢼𦭜㭎枍𬨂𬀩𬀪旿昄昒昈咉岞峂㟃𬬩钖牥侁佸㑊侂佽郈舠攽肸狉狝饳炌泂泃泇峃祋祊𫍣𬣳𬩽鸤弢弨陑𬮿陎𬯀妭姈𫰛叕𬳵𬳶䌹𫠊㛃玶珇珋珌玿韨垚垯垙垍耇鿍垎垟垏荁荙茽荄𬜬荓𦰡㭕柷栐柖郚剅䴓砆耏䶮昺𪾢昽盷咡咺昳昣昫昡昪虷虸哃峘峛𪨰峗峧帡钘𬬮𬬱俫俙垕衎侴鸧𦙶胈胣飐饻庤炟㶲洭洓洿㳚洑洢洈洺洨㳘洴洣恔宬扂袆祏叚娀姞姱姤姽枲绖骃𬘡𬳽𬘩𫄧珛珹玼𪟝珦珫𬍤珢珕珝𫭼垾垿埌茝𬜯鄀莝䓖莙栻𬂩梴栒𫠆砵砫硁翃郪𨐈辀𬌗剕晊唝冔晐畖蚄蚆𫑡峿𪨶帨崀𬬸𬬹𬬿𬭁甡倻倴倕𫢸倓倧衃虒舥朓虓鱽峱𫗧竘羖烠烔烶烻𬊈涍浭涄涢涐浰浟浛涘悈悢𬒈宧窅窊窎扅扆袯隺堲疍𨺙砮㛚翂剟𬳿𫄨绤骍𬘫䂮琎琄琈琀堎堐埫堌𫮃㙍萚䓫勚菂菍菼䓨菉梽桲梾桯梣梌桹硔鿎硊硍勔䴕龁逴翈㫰蛃蚲𬟽啴䎃崒崌崡铏𫓯𫟹铚牻笯偡偁㿠鄅偓舲鸼悆鄃瓻䝙脟鱾猇𠅤庱庼痓䴔羕焆焌𬇹淟淜淴湴涴𬍡㥄惛惔悰惙寁𬤇𫍯祲𬤊𫍲谞弶𬯎婞婼媖婳婍婌婫婤婘𬘬𬘭𬴂𫘦𫟅𬘯骕𫘧珷琡琟琔琭堾堼揕㙘堧堨塅𪣻𡎚惎萳靬葴鄚蓇葰鄑葖萹棤棽棫椓椑𬃊椆棓棬棪𬷕酦奡皕詟𫐐辌棐龂𬹼睎晫晪晱𧿹斝崶嵁𫶇嵅崿嵚翙𫖮圌圐赒𨱇𫓶𬭎颋稌筀筜傃傉翛傒脿䐃腒𬱟鲃猰𫛭㺄馉凓𫷷廆鄌遆旐𬮱焞𬊤欻𣸣溁湝渰㴔溠溇湑溞敩棨扊婻媆媞㛹媓媂矞𬴃𫘨缐骙瑃瑓瑅瑆䴖瑖瑝瑔𤧛瑂嶅瑑赪摛塝搒蒱蒨蓏蓢蓂榃楒楩椸歅𬪩碃碏𬒔碈䃅鄠辒𬨎𫐓䣘暕鹍㬊暅跱蜐蜎嵲赗𫓹锧𬭚稑䅟𬕂筼筶筦筤艅谼貆腨腯鲉鲌䲟𬶋𬶍鲏猺飔觟𦝼馌裛鹒鄜麀阘𫔶煁煃煋煟煓溍溹滆溦溵漷滧滍愭慆𫌀禋禘禒鹔𫖳嫄戣𫘪𫘬缞耤瑧𫞩瑨瑱斠摏墕墈墐摴𡐓𪤗靽蔈蔊榰槚𣗋槜疐𬸘碶䃎𬒗碨𥔲𫚖䴗鹖㬎幖嶍圙𨱏𬭤镃鹙箖僔㙦𫚕鲖鲗鲘𬶐𬶏𩽾飗𬸚凘廙鲝鄫漹潩漼漴㽏漈漋漻慬㮾𬤝隩嫕嫭𬙂㻬璆墣墡蔃鼒槱鹝磏殣霅暵暶踦䗖蝘噇噀嶲嶓㠇嶟嶒镈镋𬭩䴘艎𩾃鲪觭鹠熛潖㵐澛瑬潽潾潏憭憕𬸣戭褯禤𫍽嫽𬴊璥璲璒薳黇𬞟薢橞橑𥕢磜豮𫟦𬺈𫠜虤曌㬚蹅踶䗛疁㠓幪𪩘嶦𬭬𨱑𬭯穄篯簉衠鲯𫗴亸𬸦羱燚燏濋澽澭澼翯𫄷璱𤩽璬璮髽擿薿櫆檞醨繄磹磻瞫蟏㘎𫔍𬭸𨱔𬭼𫔎矰穙穜穟簕簃儦魋斶𬸪䲠𬶟鲾𬶠鲿鳂鳈鳉䗪襚𬶨螱嬥𦈡𫄸瓀鬶爇鞮𬟁藟藦藨鹲礌𥖨蹢蹜蟫䗴嚚髃酂馧簠簝簰鼫鼩䲢鳑鳒鹯𦒍旞翷䎖瀔瀍瀌襜䴙𬙊嚭㰀鬷蠋翾儴𬶭𩾌鳚鳛麖彟鬒蘘欂甗𨟠巇酅犨𬶮𨭉㸌爔瀱瀼襫骦𬙋耰𤫉𬺓鼱鳠鳡鳣爟爚灈韂糵礵鹴皭鳤亹𫚭玃醾齇觿朘塃葓湨塈塮檵礳耲㗒㗳㞗㦸㧸㨃㩜㷧䁓䁥䂻䉵䒷䗩䚎䜇䟴䭾䰄䰻䰾䱋䱗俲俽傦僙刟剗剠剨劚勑勡匬匲厪厫呩咹唨啳嗻嘑嘠嘷嚞圕坆坧埦堦塳墰妷婣峑嵆嵗嶎帒彍徤徺悞惽慜憜懢戹拕捬擪斅斆昷晈朌朥枬柹椬椾槀槩橒橺檝檲櫊欵歒毺泎洤涹湏濚炁烕焴煱煶牐牕猂猨獱琹畺瘇皡盌眫磓磘礮秌秔稭窻竉笟箣籂籑籝籰粆粦粬糚絍緵耝聛聣聦脃脌臯臶舚苐苽莾蒀蒕蘐蝱螌螥螩蟁蟖蠭袠覉覔覼詧詾譃讁贘赥趦踁踨蹵蹷躧辠遌酑酙酧酼醎醻釾鍫閗阸陁隁隖霃霡霱靝靟鞟鞺頟頮顇顖顦颴飦餹餻駚騌騐骽髗髿鬂鬉鮌鮍鰃鰟鰧鱂鱏鱓鱤鱥鴂鴓鸜麄麐麘麞麨鼂鼧齅齓齚齩龎龥𠜎𠱓𠳔𠳕𠴕𠵿𠸎𠸏𠹷𠻺𠼻𠾴𠾼𠽾𠾐𡁯𡁵𡃉𡂫𡇙𡝭𡷑𡼏𢆡𢔛𢝵𢞵𢫕𢴈𢺳𣜿𤃒𤍤𤶀𥁕𥟇𦤎𦸅𧍱𧒆𧦠𧬪𨋍𨍽𨎊𨸹𩷓𩺬𩼰𩽈𩽰𪂺𪇡𪙊𫒢𫬷𭉝𰇛鿽俋傜呯咈唎喎囍妏姵媗媜屭巿彣掯搥旂旼暐枒櫫氂澔灩焢犽瘖瘜瘝礡禕翬胇芛蠵褔譭躕辵魟鯓鯷鷴㕣梲虪媯媿巂徯怗怹挜敠朆槅槑槥溈㐂㖞㭴㾦䃚䇲䌷䎬䖬䜩䥺䦆僜刲勷匽咵哣唡唻啯垇垽夆焮牷犗痎瘄瘈皶盝眜砢硵碔稖穞窾篰篲罥聤肐胔胾菑葇蚃蜰襆觍诪谉貐踄踖踧輶銶锠闬阓阛霂颒颣饤饾馂鬐魌鯃鹓𠉂𠚤𠮟𠸁𢙐𢽾𣱝𤆢𤟯𤻊𥄨𥆧𦎓𦨭𦭌𦶟𦻘𧮪𨰾𨱍𨱎𨱓𩨂𩽼𩾇𱱿㚬㛄㛢㨗㶈㷍㼈䕒䭲亷仱侞俁倛偟傛儫咅咘喭嘒嘪圡坣妡妦姁姃姎姳娪娳婗媁媃媐嫃嫆嫈嫙嫥嬃嬑嬣嬨嬫孋孍宭寗寯峮嵵庒憓敻斳晛晸暟暻曏曣椉椲楀楟榤槶檥汘泑浿涒淂湋溎潓潣澐煚熀熲猋玅玗玴珆珓珳琁琣瑈瑒瑮瑲瑺瑽璊璵璸璻瓈瓌瓛畇硘硦祤禑秜秝笭筎箂綝綪緁茿荺莯萲蒍蒝蕥薆薾褘詅諪諴譔豑赮辳逤鈅鈜鈤鈱鈵鉌鉯銍鋊鋑錤錩錪錱鍌鍏鍱鍹鎛鎡鐈鐏鐤鑶闓顒馡騂騋驒鱻鵟鷰龘𡟚𡩋𤧟𧃽𩻸悮䒐䒏俹簁`

    </p>
</details>

- <details>
    <summary>Fixed 7 hanzi</summary>
    <p>

    - `彳爿豸𡠍槨氍繏`

    - Characters moved to their correct code points: `𡣐𭯪橔`

    </p>
</details>

- Added full Greek support: `ΆΈΉΊΌΎΏΐΪΫάέήίΰϊϋόύώ΄΅`, and redesigned `χ`

> Thanks to ZERO ([@Skr-ZERO](https://github.com/Skr-ZERO)) for the fixes above.

- Completed the Bopomofo Extended block (U+31A0..U+31BF) and the tone marks of the Taiwanese Phonetic Symbols

- Added the newly encoded Ideographic Description Characters: `⿼⿽⿾⿿㇯`

- Updated some OpenType features (`vert`, `locl`)

- Removed the `liga` feature for dashes; dashes are now handled by `ccmp` so they are also substituted in vertical text

- Added OpenType features (`halt`, `vhal`, `chws`, `vchw`)

- Added TTF font files

- Adjusted the line-height metrics following the [updated Google Fonts guidelines](https://github.com/googlefonts/googlefonts.github.io/pull/159), and added a baseline table (`BASE`)

> P/S: Selamat Hari Raya Aidilfitri!

## Ver 2.001; 20220201

- Fully switched the build process to [AFDKO](https://github.com/adobe-type-tools/afdko); the merge code now uses `mergeFonts`

- Added basic Japanese support (separate JPS/JPN builds for Std/StdN)

    - JPS is the Std build (JIS X 0208:1990, JIS90 glyphs)
    - JPN is the StdN build (JIS X 0213:2004, JIS2004 glyphs)

> Thanks to ZERO ([@Skr-ZERO](https://github.com/Skr-ZERO)) for the Japanese build process and proofreading.

> Note: the Japanese glyphs added in v2.000 are JIS83 forms, and are now fully mapped.

- Added vertical forms for Japanese small kana, with the corresponding vertical metrics (`vmtx`)

- Added OpenType features for switching Japanese glyph forms (`jp83`, `jp90`, `jp04`)

- Updated some OpenType features (`ss19`, `ss20`, `vert`, `locl`)

- *Removed RFN in SIL OFL for Google Fonts preparation*

> P/S: Happy Chinese New Year!

## Ver 2.000; 20211225

- Release fonts are now in OTF format; the build process switched to [AFDKO](https://github.com/adobe-type-tools/afdko)

- <details>
    <summary>Added 1883 hanzi, completing the hanzi in the dictionaries of frequently used Taiwanese Hokkien and Hakka words, level-5 Hong Kong common characters in the <a href="https://github.com/ichitenfont/suppchara">Hong Kong Supplementary Character List</a>, GB/T 12345, <a href="https://kanji.jitenon.jp/cat/jisdai2.html">JIS level 2</a> kanji and the IBM 32 extension characters</summary>
    <p>

    - `㐁㑁㑑㓟㓾㔂㕱㕸㖅㖸㗘㗱㘔㘛㘝㘭㜮㜷㜺㝗㝩㤉㤕㧁㧌㧎㧒㧡㧣㧻㧾㨂㨑㨨㨪㨻㩆㩗㩧㩮㪐㰵㴘㴙㷛㷮㸐㸰㼆㼓㽎㾀㾊㿭㿸㿺䀐䀯䀴䀹䁅䁯䃗䃟䆀䇶䈄䉂䌈䏡䏲䓛䓝䓪䓬䖙䖳䗁䗆䗐䘆䘥䘼䞚䟓䟘䟩䠡䢂䢍䢢䥑䦉䪴䫌䯋䰳䱛䲁䲅䲗䳍䴈䴉丱丼乂乕乢亅亊亰亶亼仭伀伃伜伡伣伨伹伻佖侊侒侘侚侫侹俉俍俔俛俤俥俶俿倅倈倢倯倲偀偂偝偰傔傪傱僊僘僫僴儁儑儖儱兊兤冏冐冓冝冦冩冾凃凅凊凖凟凩凬凴凾刄刋刐刓刔刕刜刣刦刧剉剏剱剳剺剾劄劒劔劜劦劯劼勀勠勥勼匇匤匧匳匸匼卆卌卲厓厖厰叆叇叝叺叾吂呟呧呰呴呾呿咊咜咢咥哘哢哯哱哹唅唊唌唥唩唭唶唹啀啌啹喌喐喓喞喢喤喥喨嗋嗙嗹嗺嘓噐噒噭噷嚉嚊嚔嚠嚤嚱嚵嚹嚾囃囎囓囥囮囷圀圦圷圸坉坔坙坥坱坵坺坿垈垉垞垪垬垰垳垺埀埆埇埈埓埖埣埪堽塠塰塲墘墫墲墸墹墺壗壜壥壸壻壼夊夐夘夛夬奅奒奓奛奝奣妛妺姙姼娗娚娵婬婸媌媱嫋嫐嬶嬾孅寀寃寉寘尞尠尨尪屃屓屧屶屻岦岶岺岻岼岾峅峇峣峵峺崄崋崕崘崟崠嵂嵎嵒嵓嵙嵜嵭嵳嵶嶌嶐嶢嶬嶮嶹巐巵帋幇幎幤幵庰廍廏廕廩廰廱廹弇弉弌弍弖弡弴弸彁彅彑彔彜徃徛徧忞忟忰怐怺恅恊恟恠恷悁悊悋悗悤悧悳悾悿惓惗惞惪惷愃愐愑愖愡愨愬愰愽慂慒慓慙慥慭慯慱慴慽憇憖憘憙憢憺懃懆懞懴懽戉戓戞扐扚扞扠扡扨扴扷抂抃抅抐抝抾拁拏拑拵拹挃挌挐挓挔挕挧挩挱挳挵挶挷挼捀捒捔捘捙捝捥捾掔掜掝掞掫掵揇揋揌揑揙揜揢揫揬揰揵揻搇搉搙搝搟搢搤搧搨搩摃摎摖摝摠摵撆撋撍撏撘撝撨撴擉擛擣擶擽攅攋攎攑攕攷敆敋敧敨敱斈旙旛旡昉昜昞昮昻昿晄晙晥晧晬晳暃暎暙暠暲暼暿曁曚曵曺曻朎朏朒朖朞朳朷朸朿杁杙杣杤杦杮枅枌枡枦枩枹枻柀柆柎柤柧柫柮栁栫栱栿桍桒桙桮桱桸桾梍梛梠梹梺棆棈棊棏棑棔棡棢棯椄椈椊椌椚椡椢椣椥椦椨椪椶楙楜楪楬楴楻楾榁榅榑榖榠榲榼榾槇槝槞槢槫槹槺樌樒樔樛樠樢樮樰樶橂橆橦橲橳橸檍檨檪櫁櫑櫢櫤櫼欅欉欟欱欶歁歔歕歛殀殕殗殱毟氿汢汫汯汳沊沕沚沺泙泚泝泧洘洟浡浤浱浲涖涬淏淕淰淲渕渟渧渮渹渼湜湠湢湳湶湼溂溓溚溡溿滒滮漑漖漦潗澁澂澑澣澵濔濳濵濶瀁瀇瀳灇炣烋烌烝烰烱烳焄焏焠焫焿煇煏煠煡煴煻熁熅熇熈熕熝熥熰熻燖燗燵爁爌爕爧爼牋牚牸犂犅犇犱狆狌狢猄猌猤猯獏玽珎珒珖珣珱珵珸琩琲瑢璢瓅瓧瓩瓰瓱瓲瓸甁甃甅甎甞甼畄畆畉畍畓畤畩畭畯疂疉疕疧疶疺痀痌痚痟痡痾癈癎癗癠癨癶皀皃皛皜皞皦皷皹盦盻眛眡眤眥睆睭瞆瞖瞨瞶瞹矺矻矼砄砈砛砡硓硙硞硩硴硺碆碖碪碫碯碵磆磑磟磳礆礇礑礒礰禔禝秄秡秥秪秬秮稘稙稴稾穃穉穽窞窵竍竏竑竒竓竕竚竝竡竢竧竫竰竳竵竸竻笂笐笒笘笵笶筊筥筬筰筴筺箒箘箙箚箞箟篏篶簓簔簗籏籔籖籗籘籵粃粄粅粐粡粨粩粫粭粿糀糂糋糒糘糬糺紩紵絅絈絋絏絖絙絚絜絣絪絭絽綛綟綯綷緕緖緜緟緤緪縅縒縖縡縢縺繏繐繖繝繧繷繻繿纃纉纎纐纒纻绹罇罉罍罎罠罧罶罸羂羃羇羓羮羴翆翍翸耎耞耡聟聢聨聬肨肬胐胘胠胮胿脢脥脧脽腍腘腟膁膃膋膎膓膕膤膥膭膰膵膸臈臑臙臽舦舩艀艝艢艪艸苙苝苳苺茋茖茘茣荅荍荖荢荳荵荿莀莇莚莟莵莿菎菣菶菷菻萓萠萢萣萪葈葢葮葯葹蒄蒟蒭蒻蓙蓚蓜蓪蓴蔕蕀蕋蕚蕣蕫蕰蕳薀薁薐薸藃藠藾蘂蘓蘯蘰虘蚫蚻蛬蛯蜅蜑蜺蝒蝛蝝蝟蝪蝲蝹螔螕螛螷螿蟇蟐蟧蟳蟷蠇蠎蠘蠧衂衊衒衖衵袓袗袙袚袰袵袿裃裄裈裌裖裲裵褄褌褜褝褞襀襌襍襕襭襴襷襾覂覈覊覕覥覩觝觧觱訄訒訚訷詏誂誐誾諚諟諠諡謌謴謼譀譓譛譱譿讌讙讱谺豍豼貎貛貭貮賍賰贇贌贒贔赑趒趖跁跂跈跍跔跕跙跿踈踜踰蹏蹐蹓蹔蹘蹛蹠蹧蹳蹽躄躘躙躰躱躼躽躾軁軅軆軈軣輌輙輹輼轀轌轗轜轣辧辷迌迒迚迯迵逎逧逩遉遖遧遯遰遶遹邉郤鄕酇酖酘酜酳酺醂醡醹釖釚釛釞釟釡釥釮釶釼釿鈂鈃鈆鈗鈩鈬鈼鉎鉐鉔鉙鉝鉧鉨鉮鉲鉳鉷銈銕銛銧銾鋂鋉鋐鋓鋕鋗鋙鋠鋧鋩鋹鋺鋻鋿錀錂錏錑錝錞錣錥錺錻錼鍄鍅鍈鍖鍗鍜鍠鍮鍼鎓鎝鎤鎶鎹鏀鏆鏐鏥鏸鐇鐚鐡鐱鐶鐽鑀鑁鑅鑈鑚鑞鑢鑱鑵钁铓铔铦铻锜锳锽镠镮镴镵閇閊閕閖閙閠閧闍阇阨阯陏陦隝隯隲雺霙霳霻靃靆靉靍靏靕靗靤靫靱靹鞁鞆鞐鞜鞳韈韡韲頔頕顋顗颪飃飜飮餔餝餠餤餧餬餲饂饍饐饝馝馞馦馼駮駲駸駻驎驩驫骉骎骭骿髎髜髞髢髣髱髴髷鬖鬘鬞鬪鬭魠魩魬魲魵魽鮄鮊鮏鮓鮕鮖鮗鮘鮟鮠鮡鮢鮣鮨鮰鮱鮴鮸鮹鮻鯆鯏鯑鯒鯗鯣鯮鯱鯲鰀鰄鰆鰇鰊鰌鰏鰔鰕鰗鰛鰡鰤鰮鰰鰺鱆鱇鱙鱚鱠鱰鱶鲊鲙鲬鲹鳁鳫鳬鳰鴈鴞鴪鴴鴾鵁鵄鵆鵈鵐鵙鵤鵫鵰鵺鵻鵾鶖鶤鶫鶲鶺鶿鷁鷆鷉鷏鷝鷭鷽鸊鸙鸰鸴鹀鹟鹡鹢麁麌麑麕麭麶黗黡黶鼡鼦齁齆齎齖齴齶齻龝鿏鿔鿫鿬鿭朗隆﨎﨏塚﨑晴﨓﨔凞猪益礼神祥福靖精羽﨟蘒﨡諸﨣﨤逸都﨧﨨﨩飯飼館鶴𠊎𠎷𠕆𠕇𠖄𠗻𠜱𠞩𠞭𠠃𠠝𠢕𠤎𠯗𠲿𠻗𠻘𠼮𡀔𡁶𡟓𡠍𡢃𡰪𡲢𡳞𢎙𢓜𢪱𢫏𢫦𢯭𢯾𢱋𢱤𢲴𢲸𢳆𢳪𢶀𢼌𢼛𣁳𣁴𣍐𣚺𣛮𣮈𣲩𣻸𣼎𤆬𤉙𤊶𤌍𤍒𤐙𤐰𤘅𤞚𤲍𤶃𤸁𤸱𤺅𤺪𥅾𥉌𥌚𥍉𥐵𥑮𥯟𥯥𥰔𥴊𥺆𦁄𦉎𦊓𦜆𦟪𦢊𧉟𧊅𧌄𧟰𧩣𧮙𧻴𧿁𧿬𧿳𨂾𨂿𨃩𨃰𨅔𨑨𨒇𨖕𨢑𨧀𨨏𨭆𨭎𨻶𩑝𩑾𩚨𩛩𩜄𩜰𩵱𩸙𩸶𩼧𪁎𪐞𪖐𪘒𪜶𪹚𫓧𫖯𫝏𫝘𫝛𫝺𫝻𫞼𫟂𫟧𫟷𫟼𫠛𫣆𬍛𬎆𬠖𬦰𬬭𬬻𬭊𬭛𬭳𬭶𬱖𮧵𰣻𰹬`

    </p>
</details>

- <details>
    <summary>Fixed 5 hanzi</summary>
    <p>

    - `賬溽縟蓐褥`

    </p>
</details>

- Completed the punctuation marks included in GB/T 2312

- Added Japanese half-width kana

- Fixed glyphs missed in earlier passes (chamfered corners)

- Updated some OpenType features (`smpl`, `trad`, `ss18`, `mark`)

- Added OpenType features for Chinese punctuation (`ss19` and `ss20`)

- Added an OpenType feature for switching between Simplified and Traditional regional glyphs (`locl`)

- Added some Japanese glyphs (not used yet)

## Ver 1.200; 20210831

- <details>
    <summary>Added 528 hanzi, completing Big5 levels A–C and Hong Kong common characters levels 1–4 listed in the <a href="https://github.com/ichitenfont/suppchara">Hong Kong Supplementary Character List</a>, and <a href="https://kanji.jitenon.jp/cat/jisdai1.html">JIS level 1</a> kanji</summary>
    <p>

    - `㓤㖡㖭㖿㗎㗾㧬㨘㩒㬷㬹㷫㹴䁪䐁䡍䱽乗乪乸亀仮価侭侲俵倞倹偸傌僆働兎兪円冚冧冨処凧凪剣剤剰劏劖労効勅勧勲匁匂単厳吪呉呍呑呪咇咓哋唂唓唖唚唞啅啝啩啱喛喩喰営喼嗗嗞嗱嘥噂噃噉噏噚噛噺嚡嚢嚿囲図圏圧埜埞埲埼塀塁塙塩壆壌壱壷奨妬姉姫姶姸娯婾媮嫲嬬孭孲孻宍尐尭岨峠崚嶋巌巓巣帯帰庁廃廸廻廼弐弾彞従徴悩悪惣愼戙戦戯戸戻払扤扱扲抌抜択抦拃拠拡挙挿捗捜捽掗掟掲掹掻揃揈揤揦揺揼搣搲摀摂摙摱摷撃撠撹擝擳擸攞攰斉晩暁暦曱杢杧枠柊査柾栂栃栄栞栴桝桟梖梶梼椀椙椛検楕楡楢楯楳榊榎様槙槻樖権樫橿欝歓歯歳歴毘気氷浄涙涜淥渇済渉渓溌滉滙滝潅瀄瀞瀡瀦烚焔焼煀煕熚燂燋燶燿犠狛猟獴珽瑠瑳甮甴畠畬畳畷痩癦癪発皐睘睩瞏瞓矋砕砿硏硲碕礐稲穂穏穐穣窓窰竃竜笹筈筳箆篭籙籾粁粂粋粍粛糎糭紘紬経絵継続総縁縦繊繋繍繑罫羗翫翶聡肶脇脗脳脷膉膶臓舎舗舮苅荘菫萩葎蔀蔴蔵蕗薗薫薬蛍蛽蝋蝿螆蠄衞袪袴裇覇覗覚覧訳詑読諌譲讃讐豊豖賎賛趯趷踎踭蹾躀躝軚軽輋辺辻込辿迋逓遅遡郷酔醗醤醸釈鈪鉱鉾銭鋲鋳錬鎅鎌鎭鑓鑛閪闘陥険隃隠隣隷雫雰霊鞄韮頚頬頴頼顕顚餸駅駆駈騒験騨骾髄髧髪鮋鯭鯵鰯鱲鴎鴫鴬鵞鶏鹸麯麺麿黐黙齢龬𠝹𠱁𠱸𠲖𠳏𠵝𠵱𠶧𠹶𠺘𠺝𠺢𠻹𠼭𠽌𠿪𡁜𡁻𡃁𡃶𡅅𡥼𡪲𢃇𢭃𢯊𢱑𢱕𢱢𢳂𢵌𢵧𣲷𤓓𤞭𤶸𤷪𤺧𥄫𥅈𥹉𦉘𦙅𦟌𦧲𦧺𨅝𨈇𨋢𨳊𨳍𨳒𨶙𩓥𩶘𭕫𰹲𰽣`

    </p>
</details>

- <details>
    <summary>Fixed some incorrect characters</summary> 
    <p>

    - `犧壺恙慶孺鲈贯満潺瓞踽燹`

    - Characters moved to their correct code points: `鋼嗳胪舻睏矧薛軼畲屣筵豕豚翺`

    </p>
</details>

- Added Japanese kana

- Completed full [Adobe Latin 1](https://adobe-type-tools.github.io/adobe-latin-charsets/adobe-latin-1.html) and [GF Latin Core](https://github.com/googlefonts/gftools/blob/main/Lib/gftools/encodings/GF%20Glyph%20Sets/GF-latin-core_unique-glyphs.nam) Latin coverage

- Refined some glyphs (https://github.com/NightFurySL2001/WD-XL-font/issues/1)

- Fixed glyphs missed in earlier passes (chamfered corners)

- Removed `name` table entries 16/17 (SC/TC) so that some Adobe software can load the font

- Added stylistic set names

- Updated some OpenType features (`smpl`, `trad`)

## Ver 1.110; 20210101

- <details>
    <summary>Added 1 hanzi</summary>
    <p>

    - `廐`

    </p>
</details>

- <details>
    <summary>Fixed 6 hanzi</summary>
    <p>

    - `廄舉擧譽櫸遺`

    </p>
</details>

- Fixed glyphs missed in earlier passes

- Updated some OpenType features (`smpl`, `trad`)

## Ver 1.100; 20201231

- <details>
    <summary>Added 4 hanzi</summary>
    <p>

    - `逹簒噁𫫇`

    </p>
</details>

- <details>
    <summary>Fixed 27 hanzi</summary>
    <p>

    - `港巷起熵達噠撻躂鄉薌既厩嘅慨暨概溉即唧櫛癤節鯽鲫嚼爝爵`

    </p>
</details>

- Revised and unified glyphs (chamfered corners)

- Updated some OpenType features (`smpl`, `trad`, `dlig`)

- Added the Western ellipsis and middle dot to the Western punctuation set (`ss18`; `ss19` and `ss20` are reserved for Chinese punctuation)

## Ver 1.000; 20201225

Official release of WD-XL Lubrifont SC/TC.  

- <details>
    <summary>Added 589 hanzi</summary>
    <p>

    - `䆁丟並亙仼伋伕佈佔佮併佺侶侷係倖倣値倶偭偯偺偽傑傢傯僇僎僣僩僱儅儘儳儸兇兌兗內冊冑冪凈凜別刪剋剎剝剷劻勗勣勦勳勻卬卹卻吋吳吶吿呂呎咍咾唸啗啟啣喚喫嘐噓噹嚥嚮囉囌囪堉塡塭塽墦壎夠奐奧奭姅姍姦姪娛媠媼嫺嬝嬤孃孆宂宮屆屘屜屝峩峯崁崙崢嶔嶽巉巖帟廁廂廄廈廚廝弒弔強彆彊彙彥彫彿徬忼怱恆恥恵悅悽愒慄慇慍慼懍戩戶抆拋捨捲掙掛採換揹搆搖搾撐撚撢擡擧擭攜敍敎敔敘昐昤晅晉晞暍暘暱暸曆朮杗枏枓枱枴柵柺栘桿梂梔梡梱梿棄棲棻楛榣榦槓槤槨樑橫橾檮檯櫂櫈櫥櫺欐歎歜歿殼毀毚毬氊氳氾汍汎汙汚決沍沒沖沘沬況泏泜洩洶洸浥浬涊涼淒淚淨淯淸渙減湊湣湧湩湲準溫溼滷滾潛潟潠潥澦澴濩濬瀋瀰災為煆煙煥燄燉燐燬燸燻爭牀牆牴犛犾猙獎玆玨珮琯琺瑤瑯璘璿瓖甕產甦甽畧異疊疎疢痠痲痳痺瘉瘓瘺癡癥皰盜盪眾睏睜睪瞇瞋矇矓砠砲硃硿祐祕祿禇禿秈稅稈稜稟穇穋穠穫窯筍箄箇箏箠篛篠簑簷籐籣籤籥籲粵粺糉糢糰絃絕絛絰綑綠綵線緻緼縕縯縴縿繃繈繙繡繦繫纔缊缽罈罣罵羋羨羶翺耑聴脈脣脤脩脫脰腳臟臢臥艶芣茲荊菴蒞蓆蔆蔔蔥薑薶藷蘊蘗虛虯蛻蝨蠍蠏蠔衹袊袞袮裡裯製複褕褟褽襃襬覜觔觼訏訑託訢註証詖詠詨詻誌誧說謠譁譆譌譟讚谿豎豔豬豭貍貓賸贓贗跡跦跼踡踫蹚蹟蹤躂躭軏軗輓輭迆迴迺週遊遙遝郃鄗鄘醃醜醞醱釆釐釦釭鈇鉋鉤鉼銲銳錄錡錶鍊鍚鎔鎗鏽鐫鑑鑤鑪閒閤閱闆阬陜陞隄隻雊雋雞霑霤靜靦靭鞦韁韆韹韻頫頹顏颱颳颺飢餚餵餽騵髮鬆鬍鬚鬨鬱鯈鱷鴃鴒鶸鹹麪麫麵麹麼黃黴鼇鼈鼕鼴齣齧𤂽𧬨`

    </p>
</details>

- <details>
    <summary>Fixed some incorrect characters in <a href="https://www.github.com/googlefonts/zcool-qingke-huangyou">ZCOOL QingKe HuangYou</a></summary> 
    <p>

    - `盧鷳癇轂濕巔癲縧勖帽瑁冒冕竪夂曰勘載狀瘳禛醛蹒祇暢溧篥擊睞嘜麥麩麴褻戇賜類槔縣懸聽繈譏陝懣滿瞞蟎蹣顢偬與鹧颧鈰鬧衿軎` (excerpt)

    - Characters that have a proper Unicode code point were moved to it

    </p>
</details>

- <details>
    <summary>Unified the character face box and hanzi design of Traditional characters</summary> 
    <p>

    - `仏厷頁` (excerpt)

    </p>
</details>

- <details>
    <summary>Fixed some glyphs that rendered inverted (filled and hollow areas swapped)</summary> 
    <p>

    - `蜱镛癫箸铟靥` (excerpt)

    </p>
</details>

- Added punctuation marks and their vertical typesetting settings

- Added Bopomofo and the corresponding tone marks

- Added Hanyu Pinyin, Tâi-lô and Pe̍h-ōe-jī support

- Adapted the Traditional/TC version to [inherited glyph forms](https://github.com/ichitenfont/inheritedglyphs) and centred punctuation

- Added Cyrillic and Greek letters
