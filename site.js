(function () {
  'use strict';

  var LATEST = 'latest';
  var ONE_DAY = 864e5;

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  // ---- Click-to-play video, shared by the home panel and the fix pages ----
  function playVideo(btn) {
    var facade = btn.closest('.facade');
    var frame = document.createElement('iframe');
    frame.src = 'https://www.youtube-nocookie.com/embed/' + btn.dataset.video + '?autoplay=1&playsinline=1&rel=0';
    frame.title = btn.dataset.title;
    frame.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
    frame.allowFullscreen = true;
    frame.tabIndex = 0;
    facade.replaceChildren(frame);
    frame.focus();
  }

  // ---- Share button on the fix pages ----
  function shareLink(btn) {
    var url = location.href;
    var status = btn.parentElement.querySelector('.share-status');
    if (navigator.share) {
      navigator.share({ title: document.title, url: url }).catch(function () {});
      return;
    }
    navigator.clipboard.writeText(url).then(
      function () { status.textContent = 'Link copied'; },
      function () { status.textContent = url; }
    );
  }

  document.addEventListener('click', function (e) {
    var play = e.target.closest('.facade-play');
    if (play) return playVideo(play);
    var share = e.target.closest('.share-btn');
    if (share) shareLink(share);
  });

  // ---- Rendering helpers ----
  function relativeDate(iso) {
    var days = Math.floor((Date.now() - new Date(iso).getTime()) / ONE_DAY);
    if (days < 1) return 'today';
    if (days === 1) return 'yesterday';
    if (days < 30) return days + ' days ago';
    var months = Math.floor(days / 30);
    if (months < 12) return months + (months === 1 ? ' month ago' : ' months ago');
    var years = Math.floor(days / 365);
    return years + (years === 1 ? ' year ago' : ' years ago');
  }

  function runTime(iso) {
    var m = /^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$/.exec(iso || '');
    if (!m) return '';
    var pad = function (n) { return String(n || 0).padStart(2, '0'); };
    return m[1] ? m[1] + ':' + pad(m[2]) + ':' + pad(m[3]) : (m[2] || 0) + ':' + pad(m[3]);
  }

  function sponsoredLink(item) {
    return '<a href="' + esc(item.link) + '" rel="sponsored noopener" target="_blank">' + esc(item.name) + '</a>';
  }

  // youtube.json may still hold the older {link} shape until the next daily run.
  function gearItems(g) {
    if (g.items) return g.items;
    return g.link ? [{ name: 'The gear from this video', link: g.link }] : [];
  }

  // Dollar amounts stay off the page. Percent-off creator codes are fine.
  function codeLine(g) {
    if (!g || !g.code) return '';
    var prefix = g.deal && g.deal.indexOf('$') === -1 ? g.deal.replace('OFF', 'off') + ' with code ' : 'Code ';
    return prefix + esc(g.code);
  }

  function setVideoCount(stats) {
    if (!stats || !stats.videoCount) return;
    var count = parseInt(stats.videoCount, 10).toLocaleString('en-US');
    document.querySelectorAll('[data-stat="videos"]').forEach(function (el) { el.textContent = count; });
  }

  // ---- Home: the fix panel. Every state renders one PanelModel ----
  // PanelModel: {id, short, title, summary, kit: [{name, link}], kitNote, code,
  //              stepsHref, pill: {kind, text}}
  function modelFromFix(fix) {
    return {
      id: fix.video.id,
      short: fix.video.short,
      title: fix.title,
      summary: fix.summary,
      kit: fix.kit || [],
      kitNote: fix.kitNote,
      stepsHref: '/fix/' + fix.slug + '/'
    };
  }

  function modelFromVideo(video, gear, fix) {
    var model = fix ? modelFromFix(fix) : { summary: 'Hit play, it runs right here on the page.', kit: [] };
    var g = gear.find(function (x) { return x.id === video.id; });
    var age = Date.now() - new Date(video.publishedAt).getTime();
    model.id = video.id;
    model.short = !!video.isShort;
    model.title = video.title;
    if (!model.kit.length && g) model.kit = gearItems(g);
    model.code = codeLine(g);
    model.pill = age < 7 * ONE_DAY
      ? { kind: 'pill-new', text: 'New this week' }
      : { kind: 'pill-when', text: 'Posted ' + relativeDate(video.publishedAt) };
    return model;
  }

  function panelHtml(m) {
    var title = esc(m.title);
    var thumb = m.short
      ? '<img src="https://img.youtube.com/vi/' + m.id + '/hqdefault.jpg" alt="Video thumbnail: ' + title + '" width="480" height="360">'
      : '<img src="https://img.youtube.com/vi/' + m.id + '/maxresdefault.jpg" ' +
        'onerror="this.onerror=null;this.src=\'https://img.youtube.com/vi/' + m.id + '/hqdefault.jpg\'" ' +
        'alt="Video thumbnail: ' + title + '" width="1280" height="720">';
    var kit = m.kit.length
      ? '<ul class="kit-list">' + m.kit.map(function (k) { return '<li>' + sponsoredLink(k) + '</li>'; }).join('') + '</ul>'
      : '';
    var hasKitBlock = kit || m.kitNote;
    return '<div class="facade' + (m.short ? ' is-short' : '') + '">' + thumb +
        '<button type="button" class="facade-play" data-video="' + esc(m.id) + '" data-title="' + title + '" aria-label="Play: ' + title + '">' +
        '<span aria-hidden="true">&#9654;</span></button></div>' +
      '<div class="panel-body">' +
        (m.pill ? '<p class="' + m.pill.kind + '">' + esc(m.pill.text) + '</p>' : '') +
        '<h2 class="panel-title" id="panel-title" tabindex="-1">' + title + '</h2>' +
        '<p class="panel-summary">' + esc(m.summary) + '</p>' +
        (hasKitBlock ? '<div class="kit"><h3>What I used</h3>' + kit +
          (m.kitNote ? '<p class="kit-note">' + esc(m.kitNote) + '</p>' : '') +
          (m.code ? '<p class="kit-note">' + m.code + '</p>' : '') +
          (kit ? '<p class="disclosure">As an Amazon Associate I earn from qualifying purchases.</p>' : '') +
          '</div>' : '') +
        (m.stepsHref
          ? '<a class="btn btn-ghost" href="' + esc(m.stepsHref) + '">See the steps</a>'
          : '<a class="btn btn-ghost" href="https://www.youtube.com/watch?v=' + esc(m.id) + '">Watch on YouTube</a>') +
      '</div>';
  }

  function videoHtml(v, gear) {
    var g = gear.find(function (x) { return x.id === v.id; });
    var items = g ? gearItems(g) : [];
    var code = codeLine(g);
    return '<article class="video">' +
      '<a class="video-link" href="https://www.youtube.com/watch?v=' + esc(v.id) + '">' +
        '<img src="https://img.youtube.com/vi/' + esc(v.id) + '/hqdefault.jpg" alt="" loading="lazy" width="480" height="270">' +
        '<h3>' + esc(v.title) + '</h3>' +
      '</a>' +
      '<p class="video-meta"><span>' + esc(relativeDate(v.publishedAt)) + '</span><span>' + esc(runTime(v.duration)) + '</span></p>' +
      (items.length ? '<p class="video-kit">What I used: ' + items.map(sponsoredLink).join(', ') + (code ? '. ' + code : '') + '</p>' : '') +
      '</article>';
  }

  function shortHtml(s) {
    return '<a class="short" href="https://www.youtube.com/shorts/' + esc(s.id) + '">' +
      '<img src="https://img.youtube.com/vi/' + esc(s.id) + '/hqdefault.jpg" alt="" loading="lazy" width="480" height="360">' +
      '<span>' + esc(s.title) + '</span></a>';
  }

  function initHome(panel) {
    var chipsEl = document.getElementById('fix-chips');
    var latestChip = chipsEl.querySelector('[data-chip="' + LATEST + '"]');
    var fixes = {};
    var latest = null;
    var selected = null;

    function markChips() {
      chipsEl.querySelectorAll('[data-chip]').forEach(function (chip) {
        var on = chip.dataset.chip === selected;
        if (chip.tagName === 'BUTTON') chip.setAttribute('aria-pressed', String(on));
        else if (on) chip.setAttribute('aria-current', 'true');
        else chip.removeAttribute('aria-current');
      });
    }

    function render(model) {
      panel.classList.toggle('has-short', !!model.short);
      panel.innerHTML = panelHtml(model);
    }

    function revealPanel() {
      var heading = panel.querySelector('#panel-title');
      var head = document.querySelector('.site-head').offsetHeight;
      var tall = panel.offsetHeight > window.innerHeight - head;
      heading.focus({ preventScroll: true });
      panel.scrollIntoView({ block: tall ? 'start' : 'nearest' });
    }

    chipsEl.addEventListener('click', function (e) {
      var chip = e.target.closest('[data-chip]');
      if (!chip || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      var slug = chip.dataset.chip;
      var model = slug === LATEST ? latest : fixes[slug] && modelFromFix(fixes[slug]);
      if (!model) return;
      e.preventDefault();
      selected = slug;
      render(model);
      markChips();
      panel.classList.remove('swap');
      void panel.offsetWidth;
      panel.classList.add('swap');
      revealPanel();
    });

    fetch('/data/fixes.json')
      .then(function (r) { return r.json(); })
      .then(function (list) {
        list.forEach(function (fix) { fixes[fix.slug] = fix; });
        return fetch('/youtube.json');
      })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        setVideoCount(data.stats);
        var videos = data.videos || [];
        var gear = data.gear || [];
        var shorts = data.shorts || [];
        if (videos.length) {
          var hero = videos.find(function (v) { return !v.skipLatest; }) || videos[0];
          var fix = Object.keys(fixes).map(function (k) { return fixes[k]; })
            .find(function (x) { return x.video.id === hero.id; });
          latest = modelFromVideo(hero, gear, fix);
          // A visitor who already picked a chip or hit play keeps what they chose.
          if (selected === null && !panel.querySelector('iframe')) {
            selected = LATEST;
            render(latest);
            markChips();
          }
          // Shorts reach this list only via #feature; they never join the long-form grid.
          var rest = videos.filter(function (v) { return v.id !== hero.id && !v.isShort; });
          if (rest.length >= 4) {
            document.getElementById('video-grid').innerHTML = rest.slice(0, 6)
              .map(function (v) { return videoHtml(v, gear); }).join('');
          }
        }
        if (shorts.length) {
          document.getElementById('shorts-row').innerHTML = shorts.slice(0, 6).map(shortHtml).join('');
        }
        if (!latest) latestChip.hidden = true;
      })
      .catch(function () { latestChip.hidden = true; });

    var form = document.getElementById('stickerForm');
    var note = document.getElementById('formNote');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var btn = form.querySelector('button[type="submit"]');
      var original = btn.textContent;
      btn.textContent = 'Sending...';
      btn.disabled = true;
      note.className = 'form-note';
      fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' }
      }).then(function (res) {
        if (!res.ok) throw new Error('failed');
        form.reset();
        note.textContent = 'Got it. Check your mailbox soon. Let’s get it done!';
        note.className = 'form-note show ok';
      }).catch(function () {
        note.textContent = 'Something broke (fitting, right?). Please try again in a minute.';
        note.className = 'form-note show err';
      }).finally(function () {
        btn.textContent = original;
        btn.disabled = false;
      });
    });
  }

  var panel = document.getElementById('fix-panel');
  if (panel) {
    initHome(panel);
  } else {
    fetch('/youtube.json')
      .then(function (r) { return r.json(); })
      .then(function (data) { setVideoCount(data.stats); })
      .catch(function () {});
  }
})();
