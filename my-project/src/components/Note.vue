<template>
  <div class="root">
    <div class="top-line clearfix short">
      <p class="online-statement">正在协同编辑的用户数: {{onlines}}人</p>
      <div class="save-statement" v-on:click="saves(()=>{})">{{save.statement}}</div>
    </div>
    <div class="line short"></div>
    <div class="short"><input class="youdao-title" v-model="title"/></div>
    <div class="line short"></div>
    <div class="note-wrapper short">
      <textarea v-model="note" class="youdao-note" id="youdao-note" v-on:keydown="saveLocalState()"  v-on:input="sendLocalModified()"></textarea>
    </div>
  </div>
</template>

<script>
export default {
  name: 'note',
  data () {
    return {
      save: {
        statement: 'SAVE'
      },
      onlines: '1',
      title: 'NOTITLE',
      note: '1.Create your note here',
      history:{
        cursor: null,
        note: null
      },
      ws: null
    }
  },
  methods: {
    /*
     * @
     * @ 获取heartbeat
     * @
     **/
    heartbeat: function () {
      var that = this;
      this.saves(function () {
        setTimeout(() => {that.heartbeat();console.log('save')}, 10000);
      });
    },

    /*
     *
     * @ 保存
     *
     **/
    saves: function (cb) {
      var that = this;
      var re = RegExp('/spa/(.*)?/#/note/')
      var room = location.href.match(re)[1];
      this.save.statement = 'SAVING...';


      fetch('http://localhost:8002/api/heartbeat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: encodeURI('hash_id=' + room + '&name=' + that.title + '&sub=' + that.note + '\n'/*每一行都有换行符*/)
      }).then((res) => {
        return res.json()
      }).then((data) => {
        if (data.code === 200 || data.code === '200') {
          // 重置
          cb();
          setTimeout(() => {that.save.statement = 'SAVE';}, 1000);

          // 再拉新请求
          //setTimeout(that.heartbeat, 10000)
        }
      })
    },


    /*
     * @
     * @ 插入来自别人的修改
     * @
     **/
    insertAtCaret: function (myValue, pos) {
      var $node = document.getElementById('youdao-note');
      var that = this;
      if (document.selection) {
        /*
        this.focus();
        sel = document.selection.createRange();
        sel.text = myValue;
        this.focus();
        */
        console.log('ie');
      }
      else {
        if ($node.selectionStart >= pos) {
          //var scrollTop = $node.scrollTop
          var startPos = $node.selectionStart;
          var endPos = $node.selectionEnd;
          $node.value = $node.value.substring(0, pos) + myValue + $node.value.substring(pos, $node.value.length);
          //this.focus();
          $node.selectionStart = startPos + myValue.length;
          $node.selectionEnd = startPos + myValue.length;
          that.note = $node.value;
        }
        else {
          var startPos = $node.selectionStart;
          var endPos = $node.selectionEnd;
          $node.value = $node.value.substring(0, pos) + myValue + $node.value.substring(pos, $node.value.length);
          $node.selectionStart = startPos;
          $node.selectionEnd = startPos;
          that.note = $node.value;
        }
      }
    },


    /*
     * @
     * @ 切除来自别人的修改
     * @
     **/
    cutAtCaret: function (range, pos) {
      var $node = document.getElementById('youdao-note');
      var that = this;
      if (document.selection) {
        console.log('ie');
      }
      else {
        if ($node.selectionStart >= pos) {
          //var scrollTop = $node.scrollTop
          var startPos = $node.selectionStart;
          var endPos = $node.selectionEnd;
          $node.value = $node.value.substring(0, pos - range) + $node.value.substring(pos, $node.value.length);
          //this.focus();
          $node.selectionStart = startPos - range;
          $node.selectionEnd = startPos - range;
          that.note = $node.value;
        }
        else if ($node.selectionStart >= pos - range && $node.selectionStart < pos) {
          var startPos = $node.selectionStart;
          var endPos = $node.selectionEnd;
          $node.value = $node.value.substring(0, pos - range) + $node.value.substring(pos, $node.value.length);
          $node.selectionStart = pos - range;
          $node.selectionEnd = pos - range;
          that.note = $node.value;
        }
        else {
          var startPos = $node.selectionStart;
          var endPos = $node.selectionEnd;
          $node.value = $node.value.substring(0, pos - range) + $node.value.substring(pos, $node.value.length);
          $node.selectionStart = startPos;
          $node.selectionEnd = startPos;
          that.note = $node.value;
        }
      }
    },


    /*
     *
     * @ 查询光标位置
     *
     */
    getCursorPos: function () {
      var CaretPos = 0; // IE Support
      var ctrl = document.getElementById('youdao-note');
      if (document.selection) {
        var Sel = document.selection.createRange ();
        ctrl.focus ();
        Sel.moveStart ('character', -ctrl.value.length);
        CaretPos = Sel.text.length;
      }
      // Firefox support
      else if (ctrl.selectionStart || ctrl.selectionStart == '0') {
        CaretPos = ctrl.selectionStart;
      }
      return (CaretPos);
    },

    /*
     * @
     * @ 处理并发送来自我的修改事件
     * @
     **/
    saveLocalState: function () {
      this.history.cursor = this.getCursorPos();
      this.history.note = this.note;
    },

    /*
     * @
     * @ 处理并发送来自我的修改事件
     * @
     **/
    sendLocalModified: function () {
      var now_cursor = this.getCursorPos();
      var now_note = this.note;
      var type;// + or -
      var change = '';
      var range;

      /**
       * @
       * @ 判断修改方式
       * @
       **/
      if (now_cursor > this.history.cursor) {
        change = now_note.substring(this.history.cursor, now_cursor);
        console.log('+ ' + change)
        type = '+';
        range = now_cursor - this.history.cursor;
      }
      else {
        change = this.history.note.substring(now_cursor, this.history.cursor);
        console.log('- ' + change)
        type = '-';
        range = this.history.cursor - now_cursor;
      }

      //发送修改
      this.ws.send(JSON.stringify({
        type: type,
        range: range,
        pos: this.history.cursor,
        change: change
      }));

      // save this timming
      this.history.cursor = this.getCursorPos();
      this.history.note = this.note;
    },


    fetchNote: function () {
      var that = this;
      var re = RegExp('/spa/(.*)?/#/note/')
      var room = location.href.match(re)[1];
      fetch('/api/get-note/' + '?hash_id=' + room).then((res) => {
        return res.json()
      }).then((data) => {
        data = data.data;
        this.title = data.name;
        this.note = data.sub;
      })
    },

    /*
     * @
     * @ init
     * @
     **/
    init: function () {
      var that = this;
      var re = RegExp('/spa/(.*)?/#/note/')
      var room = location.href.match(re)[1];
      var ws = new WebSocket("ws://localhost:8002/api/ws/echo/" + room);
      var wsmsg;
      ws.onopen = function() {
         ws.send(JSON.stringify({'type': 'cookie', 'mycookie': document.cookie}));
      };
      ws.onmessage = function (evt) {
        wsmsg = JSON.parse(evt.data);
        if (wsmsg.type === '+') {
          that.insertAtCaret(wsmsg.change, wsmsg.pos)
        }
        else if (wsmsg.type === '-') {
          that.cutAtCaret(wsmsg.range, wsmsg.pos)
        }
        //拿到的是cookie
        else if (wsmsg.type === 'onlines') {
          that.onlines = wsmsg.count;
        }
      };
      this.ws = ws;
      this.fetchNote();
      setTimeout(() => {this.heartbeat();}, 5000);
    }
  },

  beforeMount: function () {
    console.log('init');
    this.init();
    //
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
/**
 * @
 * @ youdao
 * @
 **/
.clearfix:after{content:".";display:block;height:0;clear:both;visibility:hidden}
.clearfix{*+height:1%;}

.root .top-line {
  height: 50px;
  display: block;
}

.root .top-line .save-statement:hover {
  color: #41b883;
  border: solid 1px #41b883;
}

.root .top-line .save-statement:active {
  background-color: #41b883;
  border: solid 1px #FFF;
  color: #FFF;
}
.root .top-line .online-statement {
  color: #CCC;
  float: left;
  margin: 20px 0 0 5px;
  font-size: 16px;
  line-height: 20px;
}
.root .top-line .save-statement {
  margin: 10px 20px 0 10px;
  border: solid 1px #EEE;
  display: inline-block;
  border-radius: 6px;
  line-height: 30px;
  cursor: pointer;
  padding: 0 10px;
  float: right;
  color: #CCC;
}

.root .line {
  height: 1px;
  border: none;
  display: block;
  background-color: #EEE;
}

.root .short {
  margin: 0 10%;
}
.root .youdao-title {
  font-weight: bolder;
  text-align: center;
  margin: 10px auto;
  line-height: 30px;
  font-size: 30px;
  outline: none;
  border: none;
  color: #333;
}

.root .note-wrapper {
  display: block;
}


.root .note-wrapper .youdao-note {
  color: #333;
  width: 100%;
  border: none;
  resize: none;
  margin: auto;
  height: 900px;
  outline: none;
  display: block;
  padding: 0px 0;
  font-size: 14px;
  padding: 10px 0;
  text-align: center;
}





h1, h2 {
  font-weight: normal;
  line-height: 16px;
  font-size: 16px;
  margin: 10px 0;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}
</style>
