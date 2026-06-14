import { CheckCircle, RefreshCw, Send, XCircle } from "lucide-react";
import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

import { lockersApi, releaseRequestsApi } from "../api/modules";
import DataTable from "../components/DataTable";
import MessageBox from "../components/MessageBox";
import PageHeader from "../components/PageHeader";
import StatusBadge from "../components/StatusBadge";

const initialForm = { locker_cell: "", reason: "" };

export default function ReleaseRequestPage() {
  const location = useLocation();
  const preselectedCell = location.state?.lockerCellId;
  const [form, setForm] = useState(preselectedCell ? { locker_cell: String(preselectedCell), reason: "" } : initialForm);
  const [cells, setCells] = useState([]);
  const [requests, setRequests] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [reviewing, setReviewing] = useState(null);
  const [reviewForm, setReviewForm] = useState({ reviewer: "管理员", review_remark: "" });

  const load = async () => {
    setError("");
    try {
      const [cellData, requestData] = await Promise.all([
        lockersApi.list(),
        releaseRequestsApi.list(),
      ]);
      setCells(cellData);
      setRequests(requestData);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const occupiedCells = cells.filter(
    (c) => c.status !== "empty"
  );

  const updateField = (event) => {
    setForm({ ...form, [event.target.name]: event.target.value });
  };

  const submit = async (event) => {
    event.preventDefault();
    setMessage("");
    setError("");
    try {
      await releaseRequestsApi.apply({
        locker_cell: Number(form.locker_cell),
        reason: form.reason,
      });
      setMessage("释放申请已提交，等待管理员审批。");
      setForm(initialForm);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const review = async (id, action) => {
    setError("");
    try {
      const fn = action === "approve" ? releaseRequestsApi.approve : releaseRequestsApi.reject;
      await fn(id, reviewForm);
      setReviewing(null);
      setReviewForm({ reviewer: "管理员", review_remark: "" });
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <>
      <PageHeader
        title="远程释放申请"
        description="客服申请释放柜格，填写原因后由管理员确认释放。"
        action={
          <button className="ghost" onClick={load}>
            <RefreshCw size={16} />刷新
          </button>
        }
      />
      <MessageBox type="success">{message}</MessageBox>
      <MessageBox type="error">{error}</MessageBox>

      <section className="work-grid">
        <form className="panel form-panel" onSubmit={submit}>
          <h2>申请释放柜格</h2>
          <label>
            柜格
            <select name="locker_cell" value={form.locker_cell} onChange={updateField} required>
              <option value="">请选择柜格</option>
              {occupiedCells.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.zone}-{c.code}（{c.status_label}）
                </option>
              ))}
            </select>
          </label>
          <label>
            申请原因
            <textarea
              name="reason"
              value={form.reason}
              onChange={updateField}
              rows={3}
              required
              style={{ width: "100%", border: "1px solid #cfd8e3", borderRadius: 6, padding: "10px 11px", minHeight: 40, font: "inherit", resize: "vertical" }}
            />
          </label>
          <button type="submit">
            <Send size={18} />提交申请
          </button>
        </form>

        <section className="panel">
          <div className="panel-title">
            <h2>申请记录</h2>
          </div>
          <DataTable
            rows={requests}
            columns={[
              { key: "cell_code", title: "柜格" },
              { key: "cell_zone", title: "区域" },
              { key: "reason", title: "原因" },
              { key: "applicant", title: "申请人" },
              {
                key: "status",
                title: "状态",
                render: (row) => <StatusBadge status={row.status} label={row.status_label} />,
              },
              { key: "reviewer", title: "审批人" },
              { key: "review_remark", title: "审批备注" },
              {
                key: "created_at",
                title: "申请时间",
                render: (row) => (row.created_at ? new Date(row.created_at).toLocaleString("zh-CN") : ""),
              },
              {
                key: "actions",
                title: "操作",
                render: (row) =>
                  row.status !== "pending" ? (
                    <span className="badge gray">已处理</span>
                  ) : reviewing === row.id ? (
                    <div className="review-inline">
                      <input
                        placeholder="审批备注（选填）"
                        value={reviewForm.review_remark}
                        onChange={(e) => setReviewForm({ ...reviewForm, review_remark: e.target.value })}
                      />
                      <button className="ghost" onClick={() => review(row.id, "approve")}>
                        <CheckCircle size={15} />通过
                      </button>
                      <button className="ghost danger" onClick={() => review(row.id, "reject")}>
                        <XCircle size={15} />拒绝
                      </button>
                      <button className="ghost" onClick={() => setReviewing(null)}>
                        取消
                      </button>
                    </div>
                  ) : (
                    <div className="row-actions">
                      <button className="ghost" onClick={() => setReviewing(row.id)}>
                        审批
                      </button>
                    </div>
                  ),
              },
            ]}
          />
        </section>
      </section>
    </>
  );
}
